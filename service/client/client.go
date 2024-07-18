package client

import (
	"crypto/rand"
	"fmt"
	"net"
	"os"
	"time"
)

const (
	REMOTE_PORT = "30010"
)

func Run(SERVER string, size int, ifname string, debug bool) {
	remoteAddr, err := net.ResolveTCPAddr("tcp", SERVER+":"+REMOTE_PORT)
	exit_on_error(err)

	buf := createRandomData(size)
	c := 0
	for {
		iface, err := net.InterfaceByName(ifname) // Get interface spec
		// If interface exists, then send info
		if err == nil {
			address, _ := iface.Addrs() // Get its address
			ip := &net.TCPAddr{         // Convert to IPv4 address only
				IP: address[0].(*net.IPNet).IP,
			}
			dialer := net.Dialer{LocalAddr: ip} // Create a dialer from a specific IP address.

			conn, err := dialer.Dial("tcp", remoteAddr.String())
			exit_on_error(err)
			ping(conn, buf)
			if debug {
				fmt.Printf("[%d] Sent data | Timestamp: %s\n", c, time.Now().UTC().Format("15:04:05"))
			}
			c++
		} else {
			fmt.Printf("No interface with name %s\n", ifname)
		}
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

func createRandomData(size int) []byte {
	data := make([]byte, size)
	rand.Read(data)
	return data
}
