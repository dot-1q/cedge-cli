package client

import (
	"crypto/rand"
	"fmt"
	"net"
	"os"
	"time"
)

const (
	REMOTE_HOST = "10.255.32.163"
	REMOTE_PORT = "30010"

	PING_PERIOD = 10 * time.Millisecond
)

func Run() {

	remoteAddr, err := net.ResolveTCPAddr("tcp", REMOTE_HOST+":"+REMOTE_PORT)
	exit_on_error(err)

	conn, err := net.Dial("tcp", remoteAddr.String())
	exit_on_error(err)

	buf := createRandomData()
	for {
		time.Sleep(PING_PERIOD)
		ping(conn, buf)
	}
}

func ping(conn net.Conn, msg []byte) {
	_, err := conn.Write(msg)
	exit_on_error(err)
}

func exit_on_error(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func createRandomData() []byte {
	data := make([]byte, 2048)
	rand.Read(data)
	return data
}
