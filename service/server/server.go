package server

import (
	"fmt"
	"io"
	"net"
	"os"
	"time"
)

const (
	HOST = "0.0.0.0"
	PORT = "8888"
)

func Run(debug bool) {
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
			go echo(conn, &connection, debug)
		}
	}
}

func echo(conn net.Conn, connection *int, debug bool) {
	defer conn.Close()

	for {
		buf := make([]byte, 10240)
		_, err := conn.Read(buf)
		conn.SetDeadline(time.Now().Add(1000 * time.Millisecond))
		if err == io.EOF {
			return
		}
		if err != nil {
			fmt.Println("Error reading:")
			fmt.Println(err)
			return
		}
		if debug {
			fmt.Printf("[%d] Got data from: [%s]\n", *connection, conn.RemoteAddr().String())
		}
		*connection++
	}
}

func exit_on_error(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
