package server

import (
	"fmt"
	"io"
	"net"
	"os"
)

const (
	HOST = "localhost"
	PORT = "8888"
)

func Run() {
	addr, err := net.ResolveTCPAddr("tcp", HOST+":"+PORT)
	exit_on_error(err)

	listener, err := net.ListenTCP("tcp", addr)
	exit_on_error(err)

	fmt.Println("Listening on port", PORT)

	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println(err)
		} else {
			go echo(conn)
		}
	}
}

func echo(conn net.Conn) {
	defer conn.Close()
	defer fmt.Println("")

	fmt.Printf("Connected to: %s\n", conn.RemoteAddr().String())

	for {
		buf := make([]byte, 512)
		_, err := conn.Read(buf)
		if err == io.EOF {
			return
		}
		if err != nil {
			fmt.Println("Error reading:")
			fmt.Println(err)
			continue
		}

		fmt.Println(fmt.Sprintf("[%s]", conn.RemoteAddr().String()), string(buf))

		_, err = conn.Write(buf)
		if err != nil {
			fmt.Println("Error writing:")
			fmt.Println(err)
			continue
		}
	}
}

func exit_on_error(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
