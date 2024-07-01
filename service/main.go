package main

import (
	"flag"
	"fmt"
	"service/client"
	"service/server"
)

func main() {
	runtype := flag.String("type", "none", "Type of module to run. Either server or client")

	flag.Parse()

	switch *runtype {
	case "server":
		fmt.Println("Starting server:")
		server.Run()
	case "client":
		fmt.Println("Starting client:")
		client.Run()
	default:
		fmt.Println("Specify whether `client` or `server` type")
	}
}
