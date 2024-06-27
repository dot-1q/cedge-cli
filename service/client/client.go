package client

import (
	"fmt"
	"net"
	"os"
	"time"
)

const (
	REMOTE_HOST = "localhost"
	REMOTE_PORT = "8888"

	PING_PERIOD = 1 * time.Second
)

func Run() {

	remoteAddr, err := net.ResolveTCPAddr("tcp", REMOTE_HOST+":"+REMOTE_PORT)
	exit_on_error(err)

	conn, err := net.Dial("tcp", remoteAddr.String())
	exit_on_error(err)

	for {
		time.Sleep(PING_PERIOD)
		ping(conn, "hello from client")
	}
}

func ping(conn net.Conn, msg string) {
	_, err := conn.Write([]byte(msg))
	exit_on_error(err)

	fmt.Println("Sent", msg)

	buf := make([]byte, 512)
	_, err = conn.Read(buf)
	exit_on_error(err)

	fmt.Println("Got ", string(buf))
}

func exit_on_error(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
