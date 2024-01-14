#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
import socketserver
import xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging


def loadMahm():
    # https://www.geeksforgeeks.org/xml-parsing-python/
    # https://stackoverflow.com/questions/44708134/how-to-convert-a-file-rss-to-xml-in-python
    url = 'http://localhost:82/mahm'
    user = 'MSIAfterburner'
    password = '17cc95b4017d496f82'
    content = ''
    with requests.Session() as session:
        session.auth = (user, password)
        resp = session.get(url, timeout=0.5)
        content = resp.content
    return content


def parseXml(content):
    # print("content :: ", content)
    root = ET.fromstring(content)
    metrics = []

    for child1 in root:
        # print("child1.tag:", child1.tag)

        if child1.tag == "HardwareMonitorEntries":
            for hardwareMonitorEntry in child1:
                if hardwareMonitorEntry.tag == "HardwareMonitorEntry":
                    # print('hardwareMonitorEntry[0]:', hardwareMonitorEntry[0].text)
                    metric_name = ''
                    metric_help = ''
                    metric_data = ''
                    metric_tags = []
                    for child2 in hardwareMonitorEntry:
                        # print(child2.tag, child2.text)
                        if(child2.tag == "srcName"):
                            metric_help = child2.text
                            # 'GPU temperature' -> 'gpu_temperature'
                            metric_name = prepareMetricName(metric_help)
                        elif(child2.tag == "data"):
                            metric_data = child2.text
                        else:
                            metric_tags.append((child2.tag, child2.text))
                    # print("metric_name:", metric_name, ", metric_data:", metric_data, ", metric_tags:", metric_tags)
                    line = "# HELP {} {}".format(metric_name, metric_help)
                    metrics.append(line)
                    line = "# TYPE {} gauge".format(metric_name)
                    metrics.append(line)
                    tags = prepareTags(metric_tags)
                    line = "{}{} {}".format(metric_name, tags, metric_data)
                    metrics.append(line)

    # print("metrics prepared with {} lines.".format(len(metrics)))
    # return news items list
    return metrics


def prepareMetricName(metric_help):
    # return re.sub(r' ', '_', metric_help).lower()
    metric_name = re.sub(r' ', '_', metric_help).lower()
    metric_name = re.sub(r'[^A-Za-z0-9_]', '', metric_name)
    metric_name = re.sub(r'__', '_', metric_name)
    metric_name = 'mahm_' + metric_name
    return metric_name


def prepareTags(metric_tags):
    line = '{'
    # line = line + ','.join('%s="%s"' % t for t in metric_tags)
    for name, value in metric_tags:
        # print("name:", name, " - value:", value)
        if value is None:
            value = 'None'
        value2 = value.replace('\\', '/')
        line = line + name + '="' + value2 + '",'
    line = line[:-1]
    line = line + '}'
    # return "{core=\"0,0\",mode=\"dpc\"}"
    return line


def savetoTxt(metrics, filename):
    # print("writing metrics to file...")
    # print(">>>>>>>>>>>>>>>>>>")
    # for line in metrics:
    #    print(line)
    # print("<<<<<<<<<<<<<<<<<<")
    with open(r'metrics.txt', 'w') as fp:
        fp.write('\n'.join(metrics))
        fp.write('\n')


class MyHttpRequestHandler(BaseHTTPRequestHandler):

    def loadMahm2(self):
        resp = self.server.session.get(url=self.server.url, timeout=0.5)
        content = resp.content
        return content

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        # https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
        # logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))

        content = self.loadMahm2()
        metrics = parseXml(content)
        self._set_response()
        output = '\n'.join(metrics) + '\n'
        self.wfile.write(output.encode())


class MyHttpServer(HTTPServer):
    url = 'http://localhost:82/mahm'
    user = 'MSIAfterburner'
    password = '17cc95b4017d496f82'
    session = None

    def __init__(self, server_address, handler_class=MyHttpRequestHandler):
        super().__init__(server_address, handler_class)
        # https://stackoverflow.com/questions/51363497/httpserver-run-requires-a-basehttprequesthandler-class-instead-an-object
        self.session = requests.Session()
        self.session.auth = (self.user, self.password)

    def __getsession(self):
        return self.session


def run(server_class=MyHttpServer, port=9183):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()




