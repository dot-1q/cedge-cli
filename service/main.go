package main

import (
	"flag"
	"fmt"
	"service/client"
	"service/server"
)

func main() {
	runtype := flag.String("type", "none", "Type of module to run. Either server or client")
	period := flag.Int("period", 100, "Delay between requests in milliseconds")

	flag.Parse()

	switch *runtype {
	case "server":
		fmt.Println("Starting server:")
		server.Run()
	case "client":
		fmt.Println("Starting client:")
		client.Run(*period)
	default:
		fmt.Println("Specify whether `client` or `server` type")
	}
}
