package server

import (
	"fmt"
	"io"
	"net"
	"os"
)

const (
	HOST = "0.0.0.0"
	PORT = "8888"
)

func Run() {
	addr, err := net.ResolveTCPAddr("tcp", HOST+":"+PORT)
	exit_on_error(err)

	listener, err := net.ListenTCP("tcp", addr)
	exit_on_error(err)

	fmt.Println("Listening on port", PORT)

	connection := 0
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println(err)
		} else {
			connection++
			go echo(conn, &connection)
		}
	}
}

func echo(conn net.Conn, connection *int) {
	defer conn.Close()
	defer fmt.Println("")

	fmt.Printf("Connected to: %s\n", conn.RemoteAddr().String())

	for {
		buf := make([]byte, 1024)
		_, err := conn.Read(buf)
		if err == io.EOF {
			return
		}
		if err != nil {
			fmt.Println("Error reading:")
			fmt.Println(err)
			continue
		}
		fmt.Printf("[%d] Got data from: [%s]\n", *connection, conn.RemoteAddr().String())
		*connection++
	}
}

func exit_on_error(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
