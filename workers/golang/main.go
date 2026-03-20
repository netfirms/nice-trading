package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/adshao/go-binance/v2"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()

	dbURL := os.Getenv("DATABASE_URL")
	symbol := os.Getenv("SYMBOL")
	if symbol == "" {
		symbol = "BTC/USDT" // Default
	}
	formattedSymbol := strings.Replace(symbol, "/", "", -1)

	// 1. Initialize DB Pool
	config, err := pgxpool.ParseConfig(dbURL)
	if err != nil {
		log.Fatal("Unable to parse DATABASE_URL:", err)
	}
	dbpool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		log.Fatal("Unable to create connection pool:", err)
	}
	defer dbpool.Close()

	fmt.Printf("🚀 Starting High-Performance Go Orderbook Worker for %s\n", symbol)

	// 2. Continuous Loop (REST parity for now, optimized with Go concurrency)
	client := binance.NewClient("", "") // No API key needed for public data
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		res, err := client.NewDepthService().Symbol(formattedSymbol).Limit(5).Do(context.Background())
		if err != nil {
			log.Printf("⚠️ Error fetching orderbook: %v\n", err)
			continue
		}

		// Calculate Mid Price or Best Bid
		if len(res.Bids) > 0 && len(res.Asks) > 0 {
			lastPrice := res.Bids[0].Price

			// Push to Postgres Cache
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
				log.Printf("❌ Failed to update cache: %v\n", err)
			} else {
				log.Printf("📥 Cached %s: %s\n", symbol, lastPrice)
			}
		}
	}
}
