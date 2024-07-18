package main

import (
	"flag"
	"fmt"
	"service/client"
	"service/server"
)

func main() {
	runtype := flag.String("type", "none", "Type of module to run. Either server or client")
	size := flag.Int("period", 1000000, "Message size")
	iface := flag.String("iface", "", "Interface name to attach to")
	sv := flag.String("server", "10.255.32.191", "Server address to send the data to")
	debug := flag.Bool("debug", false, "Print debug statments")

	flag.Parse()

	switch *runtype {
	case "server":
		fmt.Println("Starting server:")
		server.Run(*debug)
	case "client":
		fmt.Println("Starting client:")
		client.Run(*sv, *size, *iface, *debug)
	default:
		fmt.Println("Specify whether `client` or `server` type")
	}
}
