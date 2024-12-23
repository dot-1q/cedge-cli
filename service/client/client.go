package client

import (
	"crypto/rand"
	"fmt"
	"net"
	"os"
	"time"
)

func Run(server string, port string, size int, sleep int, ifname string, debug bool) {
	remoteAddr, err := net.ResolveTCPAddr("tcp", server+":"+port)
	exit_on_error(err)
	buf := createRandomData(size)

	c := 0
	for {
		addr, err := getIpv4(ifname)
		// If interface exists, then send info
		if err == nil {
			dialer := net.Dialer{LocalAddr: &net.TCPAddr{IP: addr}} // Create a dialer from a specific IP address.
			conn, _ := dialer.Dial("tcp", remoteAddr.String())
			timeout := conn.SetDeadline(time.Now().Add(1000 * time.Millisecond)) // Set 1000ms timeout
			// Continuously send data from this connection.
			if timeout == nil {
				ping(conn, buf)
				c++
				// fmt.Printf("[%d] Sent data | Timestamp: %s\n", c, time.Now().UTC().Format("15:04:05"))
			} else {
				fmt.Printf("Operation timed out | Timestamp: %s\n", time.Now().UTC().Format("15:04:05"))
			}
			time.Sleep(time.Duration(sleep * int(time.Millisecond)))
		} else {
			if debug {
				fmt.Printf("No interface with name %s\n", ifname)
			}
		}
	}
}

func ping(conn net.Conn, msg []byte) {
	_, err := conn.Write(msg)
	if err != nil {
		fmt.Println(err)
	}
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

func getIpv4(interfaceName string) (addr net.IP, err error) {
	var (
		ief      *net.Interface
		addrs    []net.Addr
		ipv4Addr net.IP
	)
	if ief, err = net.InterfaceByName(interfaceName); err != nil { // get interface
		return
	}
	if addrs, err = ief.Addrs(); err != nil { // get addresses
		return
	}
	for _, addr := range addrs { // get ipv4 address
		if ipv4Addr = addr.(*net.IPNet).IP; ipv4Addr != nil {
			break
		}
	}
	if ipv4Addr == nil {
		return net.IP{}, fmt.Errorf(fmt.Sprintf("Iface %s does not have an IPv4 address\n", interfaceName))
	}
	return ipv4Addr, nil
}
