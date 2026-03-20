package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/adshao/go-binance/v2"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
	qdb "github.com/questdb/go-questdb-client/v3"
)

func main() {
	godotenv.Load()

	dbURL := os.Getenv("DATABASE_URL")
	symbol := os.Getenv("SYMBOL")
	if symbol == "" {
		symbol = "BTC/USDT"
	}
	formattedSymbol := strings.Replace(symbol, "/", "", -1)

	// 1. Initialize DB Pools
	// PostgreSQL Pool
	config, _ := pgxpool.ParseConfig(dbURL)
	dbpool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		log.Fatal("Postgres Pool Error:", err)
	}
	defer dbpool.Close()

	// QuestDB ILP Client
	qdbHost := os.Getenv("QUESTDB_HOST")
	if qdbHost == "" {
		qdbHost = "questdb"
	}
	qdbPort := os.Getenv("QUESTDB_PORT_ILP")
	if qdbPort == "" {
		qdbPort = "9009"
	}
	qdbClient, err := qdb.NewLineSender(context.Background(), qdb.WithAddress(fmt.Sprintf("%s:%s", qdbHost, qdbPort)))
	if err != nil {
		log.Fatal("QuestDB Client Error:", err)
	}
	defer qdbClient.Close(context.Background())

	fmt.Printf("🚀 Starting SUB-MILLISECOND Go Orderbook Streamer for %s\n", symbol)

	// 2. WebSocket Listener
	wsDepthHandler := func(event *binance.WsDepthEvent) {
		if len(event.Bids) > 0 {
			lastPrice := event.Bids[0].Price
			lastAmount := event.Bids[0].Quantity

			// A. Update Postgres Cache (Real-time signal)
			cacheKey := fmt.Sprintf("price:%s", symbol)
			_, err := dbpool.Exec(context.Background(), `
				INSERT INTO realtime_cache (key, value, updated_at)
				VALUES ($1, $2, CURRENT_TIMESTAMP)
				ON CONFLICT (key) DO UPDATE SET
					value = EXCLUDED.value,
					updated_at = EXCLUDED.updated_at;
				NOTIFY realtime_update, $1;
			`, cacheKey, lastPrice)
			if err != nil {
				log.Printf("⚠️ PG Cache Error: %v\n", err)
			}

			// B. Push to QuestDB Ticks (Historical analysis)
			err = qdbClient.Table("ticks").
				Symbol("lp", "binance").
				Symbol("symbol", symbol).
				Float64Column("price", stringToFloat(lastPrice)).
				Float64Column("amount", stringToFloat(lastAmount)).
				Symbol("side", "buy").
				At(context.Background(), time.Now())

			if err != nil {
				log.Printf("⚠️ QuestDB ILP Error: %v\n", err)
			}
			qdbClient.Flush(context.Background())
		}
	}

	errHandler := func(err error) {
		log.Printf("❌ WebSocket Error: %v. Reconnecting...\n", err)
	}

	doneC, _, err := binance.WsPartialDepthServe(formattedSymbol, "5", wsDepthHandler, errHandler)
	if err != nil {
		log.Fatal("WebSocket Connection Error:", err)
	}

	<-doneC
}

func stringToFloat(s string) float64 {
	var f float64
	fmt.Sscanf(s, "%f", &f)
	return f
}
