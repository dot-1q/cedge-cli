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

	PING_PERIOD = time.Millisecond
)

func Run(PERIOD int) {

	remoteAddr, err := net.ResolveTCPAddr("tcp", REMOTE_HOST+":"+REMOTE_PORT)
	exit_on_error(err)

	conn, err := net.Dial("tcp", remoteAddr.String())
	exit_on_error(err)

	buf := createRandomData()
	c := 0
	sleepTime := PING_PERIOD * time.Duration(PERIOD*int(time.Millisecond))
	for {
		// Sleep for an amount of time passed as input.
		time.Sleep(sleepTime)
		ping(conn, buf)
		fmt.Printf("[%d] Sent data \n", c)
		c++
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
