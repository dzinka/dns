import pickle
import socket
import time

from dnslib import DNSRecord, RCODE


class dns:
    def init(self):
        self.cache = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 53))

    def load_cache(self):
        try:
            with open("data.pickle", "rb") as f:
                self.cache = pickle.load(f)
        except FileNotFoundError:
            pass

    def dump_cache(self):
        with open("data.pickle", "wb") as f:
            pickle.dump(self.cache, f)

    def lookup(self, query):
        try:
            response = query.send('8.8.8.8')
            parsed_response = DNSRecord.parse(response)
            if parsed_response.header.rcode == RCODE.NOERROR:
                q_name = query.q.qname
                answer_rr = parsed_response.rr[0]
                self.cache[q_name] = answer_rr
                print(response)
                return response
        except:
            return None

    def get_from_cache(self, query):
        q_name, q_type = query.q.qname, query.q.qtype
        result = self.cache.get(q_name)
        if result:
            response_record = DNSRecord()
            response_record.add_answer(result.rdata)
            print(result.rdata)
            return response_record.pack()
        return None

    def proceed_query(self):
        data, addr = self.sock.recvfrom(4096)
        query = DNSRecord.parse(data)
        result = self.get_from_cache(query)

        if result is None:
            result = self.lookup(query)
        if result:
            self.sock.sendto(result, addr)
            self.dump_cache()

    def start_server(self):
        self.load_cache()
        while True:
            try:
                self.proceed_query()
            except KeyboardInterrupt:
                print('Do you really want to exit?[y/n]', end=' ')
                answer = str(input())
                if answer == 'y':
                    self.dump_cache()
                    exit(0)
                else:
                    continue


server = dns()
server.start_server()


