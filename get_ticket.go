package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"net/url"
	"os/user"
	"strconv"
	"strings"
	"time"
)

const MILLI_TO_NANO int64 = 1000 * 1000

type ResponseBody struct {
	HasError     bool   `json:"HasError"`
	ErrorCode    string `json:"ErrorCode"`
	Message      string `json:"Message"`
	ReturnObject string `json:"ReturnObject,omitempty"`
}

var ticket_id int
var seat_type int
var times int
var need_tick bool
var cookie_dir string

func init() {
	flag.IntVar(&ticket_id, "tid", 0, "ticket id")
	flag.IntVar(&seat_type, "seat_type", 4, "seat type")
	flag.IntVar(&times, "times", 1, "total request times")
	flag.BoolVar(&need_tick, "tick", false, "need tick tack")
	flag.StringVar(&cookie_dir, "cookie", "./haibo.cookie", "cookie dir")
}

func (rb ResponseBody) String() string {
	var builder strings.Builder
	fmt.Fprintf(&builder, "{\n\tHasError: %t\n\tErrorCode:%s\n\tMessage:%s\n\tReturnObject:%s\n}",
		rb.HasError, rb.ErrorCode, rb.Message, rb.ReturnObject)
	return builder.String()
}

func FindDigits(b []byte) string {
	var ret []byte
	for _, c := range b {
		if c >= '0' && c <= '9' {
			ret = append(ret, c)
		}
	}
	return string(ret[:])
}

func Mill2Time(t int64) string {
	formated_time := time.Unix(t/1000, (t%1000)*1000*1000)
	return formated_time.Format("15:04:05.000")
}

func CurrMilli() int64 {
	return time.Now().UnixNano() / MILLI_TO_NANO
}

func GetServerTime(client *http.Client) (start, server, end int64, err error) {
	start = time.Now().UnixNano() / MILLI_TO_NANO
	resp, err := client.Get("https://shop.48.cn/pai/GetTime")
	end = time.Now().UnixNano() / MILLI_TO_NANO
	if err != nil {
		log.Println("Get server time failed: ", err)
		err = errors.New("Get server time failed")
		return
	}
	if resp.StatusCode != 200 {
		log.Println(resp.Status)
		err = errors.New("response status not OK")
		return
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("read body failed:", err)
		return
	}
	server_time := FindDigits(body)
	i, err := strconv.ParseInt(server_time, 10, 64)
	if err != nil {
		log.Println("convert int to str failed: ", err)
		return
	}
	server = i
	return
}

func GetCookies(path string) string {
	real_path := path
	parts := strings.Split(path, "/")
	if len(parts) > 0 && parts[0] == "~" {
		usr, _ := user.Current()
		parts[0] = usr.HomeDir
		real_path = strings.Join(parts, "/")
	}
	cookie, err := ioutil.ReadFile(real_path)
	if err != nil {
		log.Println("ReadFile(", real_path, ") failed: ", err)
		return ""
	}
	str := string(cookie[:])
	return strings.Trim(str, "\n ")
}

func GetHeaders(ticket_id, seat_type int) *http.Header {
	var header_ref strings.Builder
	fmt.Fprintf(&header_ref, "http://shop.48.cn/tickets/item/%d?seat_type=%d", ticket_id, seat_type)
	headers := &http.Header{}
	headers.Add("Connection", "keep-alive")
	headers.Add("Accept", "application/json, text/javascript, */*; q=0.01")
	headers.Add("Origin", "http,//shop.48.cn")
	headers.Add("X-Requested-With", "XMLHttpRequest")
	headers.Add("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36")
	headers.Add("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
	headers.Add("Referer", header_ref.String())
	headers.Add("Accept-Encoding", "gzip, deflate")
	headers.Add("Accept-Language", "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2")
	headers.Add("Upgrade-Insecure-Requests", "1")
	headers.Add("Cookie", GetCookies(cookie_dir))
	return headers
}

func AddTicket(client *http.Client, ticket_id int, seat_type int, headers *http.Header) *ResponseBody {
	shop := "https://shop.48.cn/TOrder/add"
	log.Println("URL:>", shop)
	data := url.Values{}
	data.Add("id", strconv.Itoa(ticket_id))
	data.Add("r", "0.5651687378367096")
	data.Add("num", "1")
	data.Add("seattype", strconv.Itoa(seat_type))
	data.Add("brand_id", "3") // 1, snh48, 2, bej48, 3,gnz48
	data.Add("choose_times_end", "-1")

	req, err := http.NewRequest("POST", shop, strings.NewReader(data.Encode()))
	if err != nil {
		log.Println("NewRequest[POST] failed:", err)
		return nil
	}
	req.Header = *headers
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Request to [%s] failed: %s\n", shop, err)
		return nil
	}
	defer resp.Body.Close()

	log.Println("response Status:", resp.Status)
	if resp.StatusCode != 200 {
		log.Println("response status not OK")
		return nil
	}
	body, _ := ioutil.ReadAll(resp.Body)
	rb := &ResponseBody{}
	err = json.Unmarshal(body, rb)
	return rb
}

func TicketCheck(client *http.Client, ticket_id int, headers *http.Header) *ResponseBody {
	shop := "https://shop.48.cn/TOrder/tickCheck"
	log.Println("URL:>", shop)
	data := url.Values{}
	data.Add("id", strconv.Itoa(ticket_id))
	data.Add("r", "0.5651687378367096")

	req, err := http.NewRequest("GET", shop, strings.NewReader(data.Encode()))
	if err != nil {
		log.Println("NewRequest[GET] failed:", err)
		return nil
	}
	req.Header = *headers
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Request to [%s] failed: %s\n", shop, err)
		return nil
	}
	defer resp.Body.Close()

	log.Println("response Status:", resp.Status)
	if resp.StatusCode != 200 {
		log.Println("response status not OK")
		return nil
	}
	body, _ := ioutil.ReadAll(resp.Body)
	rb := &ResponseBody{}
	err = json.Unmarshal(body, rb)
	return rb
}

func TickTack(client *http.Client, hour, min, sec int) bool {
	if hour == 0 {
		return true
	}
	now := time.Now()
	yy, mm, dd := now.Date()
	fmt.Println(yy, mm, dd)
	due_date := time.Date(yy, mm, dd, hour, min, sec, 0, now.Location())
	due := due_date.UnixNano() / MILLI_TO_NANO
	now_milli_sec := CurrMilli()
	if now_milli_sec > due {
		fmt.Println("curr:", Mill2Time(now_milli_sec))
		fmt.Println("exceed due date", due_date)
		return true
	}

	var rtt int64 = 0
	var dlt int64 = 0
	var rate float64 = 0.9
	first := true
	var cycle int64 = 2
	var count int64 = 15
	for i := count; i > 0; i-- {
		for CurrMilli() < due-cycle*i*1000 {
			time.Sleep(10 * time.Millisecond)
		}
		start, server, end, err := GetServerTime(client)
		if err != nil {
			return false
		}
		var est_dlt float64 = float64(server) - float64(start+end)/2
		est_rtt := float64(end - start)
		if first {
			dlt = int64(est_dlt)
			rtt = int64(est_rtt)
			first = false
		} else {
			dlt = int64(float64(dlt)*rate + est_dlt*(1-rate))
			rtt = int64(float64(rtt)*rate + est_rtt*(1-rate))
		}
		fmt.Printf("rtt=%d, dlt=%d, ", rtt, dlt)
		fmt.Printf("server time = %s, local time = %s\n",
			Mill2Time(server), Mill2Time((start+end)/2))
	}
	loop := 0
	for CurrMilli()+rtt+dlt < due {
		time.Sleep(10 * time.Millisecond)
		loop++
		if loop%100 == 0 {
			start, server, end, _ := GetServerTime(client)
			fmt.Printf("server time = %s, local time = %s\n",
				Mill2Time(server), Mill2Time((start+end)/2))
			loop = 0
		}
	}
	_, server, _, _ := GetServerTime(client)
	fmt.Println("server time =", Mill2Time(server))
	return true
}

func main() {
	flag.Parse()
	// transport layer
	var netTransport = &http.Transport{
		Dial: (&net.Dialer{
			Timeout: 5 * time.Second,
		}).Dial,
		TLSHandshakeTimeout: 5 * time.Second,
		IdleConnTimeout:     60 * time.Second,
	}
	// http client
	var client = &http.Client{
		Timeout:   time.Second * 10,
		Transport: netTransport,
	}
	if need_tick {
		TickTack(client, 20, 0, 0)
	}
	my_header := GetHeaders(ticket_id, seat_type)
	for i := 0; i < times; i++ {
		resp := AddTicket(client, ticket_id, seat_type, my_header)
		if resp == nil {
			i--
			time.Sleep(time.Second)
			continue
		}
		log.Println(resp)
		start := CurrMilli()
		var show_result_time int64 = 1
		for {
			time.Sleep(100 * time.Millisecond)
			end := CurrMilli()
			if (end - start) >= 10*1000 {
				break
			}
			if (end - start) < show_result_time*2750 {
				continue
			}
			show_result_time++
			resp := TicketCheck(client, ticket_id, my_header)
			if resp == nil {
				log.Println("TicketCheck response is nil")
			} else {
				log.Println(resp)
				if resp.ReturnObject != "" {
					break
				}
			}
		}
	}
}
