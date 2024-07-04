package client

import (
	"crypto/rand"
	"fmt"
	"net"
	"os"
	"time"
)

const (
	REMOTE_HOST = "localhost"
	REMOTE_PORT = "8888"

	PING_PERIOD = time.Millisecond
)

func Run(PERIOD int, ifname string) {
	remoteAddr, err := net.ResolveTCPAddr("tcp", REMOTE_HOST+":"+REMOTE_PORT)
	exit_on_error(err)

	iface, _ := net.InterfaceByName(ifname)
	address, _ := iface.Addrs()
	ip := &net.TCPAddr{
		IP: address[1].(*net.IPNet).IP,
	}
	dialer := net.Dialer{LocalAddr: ip}

	conn, err := dialer.Dial("tcp", remoteAddr.String())
	exit_on_error(err)

	buf := createRandomData()
	c := 0
	sleepTime := PING_PERIOD * time.Duration(PERIOD)
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
