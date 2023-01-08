#!/usr/bin/env python3

# from httpx import AsyncClient
from requests import Session
from random import choice
from bs4 import BeautifulSoup
from html import unescape
from urllib.parse import urlparse, unquote
from time import sleep, ctime
import re, sys, json, requests
# import asyncio

class Modules(Session):
	def __init__(self) -> Session:
		super().__init__()
		self.headers.update({
			"User-Agent": self.user_agent()
		})
		self.get_time = lambda : ctime().split()[-2]

	def user_agent(self):
		return choice(
			open("ua.txt").read().strip().splitlines()
		)

	def debug(self, string: str):
		print(
			"![\033[1;36m{}\033[1;0m] \033[1;31m⇒ \033[1;0m{}".format(
				self.get_time(), string.title()
			))

	def waiting(self, s):
		for x in range(s, 0, -1):
			sys.stdout.write("\r [{}] WAITING FOR : {:2d}".format(self.get_time(), x))
			sys.stdout.flush()
			sleep(1)
	
	def show_info(self, d):
		for k, v in d.items():
			self.debug(f"{k}: {v}")

	def request_proxy(self, url: str):
		return self.get(
			"http://api.scraperapi.com", params={
				"api_key": "4a8aa120323d00cc6093629d9c31ad70", 
				"url": url
			}
		)
	
	def parse(self, raw: str):
		return BeautifulSoup(raw, "html.parser")

	def bypass_ouo(self, url):
		def find_token(form):
			return form['action'], dict(map(
				lambda x: (
					x.get('id') or x.get('name'),
					x['value']), 
				form.find_all("input", 
					{"name": re.compile(r"token$")})))
		try:
			page = self.get(url)
			action, data = find_token(
				self.parse(page.text).form
			)
			self.debug(action)
			for i in range(2):
				page = self.post(action, data=data)
				action, data = find_token(
					self.parse(page.text).form
				)
				self.debug(action)
			if "ouo.io" not in page.url:
				return unquote(page.url)
			return page.url
		except Exception as e:
			if "Invalid URL" in str(e):
				print("invalid url ")
				self.waiting()
		return page

class NekoV2(Modules):

	def get_id(self, url):
		return urlparse(
			url
		).path.strip("/").split("/", 1)[-1]

	def get_hentai_list(self):
		self.debug("getting all hentai list")
		page = requests.get("https://nekopoi.care/hentai-list", headers=self.headers).text
		soup = self.parse(page)
		for li in soup.find_all(class_="title-cell"):
			yield {
				"title": li.a.text,
				"id": self.get_id(
					li.a.attrs.get("href")
				)
			}

	def get_hentai_info(self, d: dict):
		self.debug(F"getting info for: {d.get('id')}")
		page = requests.get(
			f"https://nekopoi.care/hentai/{d.get('id')}/",
			headers=self.headers).text
		soup = self.parse(page)
		if (info := soup.find(class_="listinfo")):
			d.update({
				**dict(map(
				lambda x: tuple(
					x.text.split(": ", 1) if x.text.strip() else (['',''])),
				info.find_all("li") # info list
			)), **dict(
				synopsis="".join(map(
					lambda x: x.text, 
						soup.find(class_="imgdesc").find_all("p") #synopis
				))
			)
			})

			self.show_info(d)

			if (eps :=  soup.find(class_="episodelist")): #get episode
				d["eps"] = list(map(
						lambda n: {
							str(n[0]): self.get_id(
								 n[1].a.attrs.get("href")
							),
							"release": n[1].find(class_="rightoff").text
						}, enumerate(
							eps.find_all("li"),1))
					)
			return d
		return None

	def get_download(self, title: str):
		self.debug(f"getting download list: {title}")
		page = requests.get(
			f"https://nekopoi.care/{title}/", headers=self.headers).text
		soup = self.parse(page)
		if (box := soup.find(class_="boxdownload")):
			return list(map(
				lambda d: {
					d.find(class_="name").text: list(map(
						lambda x: {
							x.text: x.attrs.get("href")}, 
						d.find_all("a"))
					)}, box.find_all(class_="liner")
			))
		return None
