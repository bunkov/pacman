# -*- coding: utf-8 -*-
from __future__ import print_function
# костыли для второго питона

import sys
import pygame
from pygame.locals import *
from math import floor
import random
import os


tile_size = 32 # Размер клетки игрового поля в пикселях (предполагается, что клетки квадратные)
map_size = 16 # Размер карты игрового поля в клетках (предполагается, что карта квадратная)
Objects = []
Ghosts = []
ITS_TEST = False
N = 0 # Кол-во запусков тестового режима

def init_window():
	pygame.init() # Инициализируем библиотеку - чтоа?
	pygame.display.set_mode((512, 512)) # Задаем размеры окна
	pygame.display.set_caption('Pacman by Alex') # Задаем загаловок окна


def draw_background(scr, img=None):
# scr - обьект класса Surface для рисования в окне приложения
# img - фоновая картинка. Если отсутствует, осуществляется заливка серым фоном
	if img:
		scr.blit(img, (0, 0)) # Координаты левого верхнего края изображения относительно того же края экрана
	else:
		bg = pygame.Surface(scr.get_size())
		bg.fill((128, 128, 128))
		scr.blit(bg, (0, 0))


class GameObject(pygame.sprite.Sprite):
	# img - путь к файлу с изображением объекта
	# x, y - координаты объекта на игровом поле
	# factor_tile - целая часть показывает, сколько тайлов занимает объект
	# symbol - символ, которым будет отображаться объект на карте
	def __init__(self, img, x, y, factor_tile, symbol):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img) # Загружаем изображение объекта
		self.tick = 0 # Время, прошедшее с момента создания объекта, в условных единицах
		self.tile_size = tile_size * floor(factor_tile)
		self.symbol = symbol
		self.set_coord(x, y)
		Objects.append(self)

	def set_coord(self, x, y):
		self.x = x
		self.y = y
		#self.screen_rect = Rect(floor(x) * self.tile_size, floor(y) * self.tile_size, self.tile_size, self.tile_size )
		# Переменная, хранящая размеры и координаты отрисовки персонажа на экране
		# Необходимость сомнительна

	def draw(self, scr):
		scr.blit(self.image, (floor(self.x) * self.tile_size, floor(self.y) * self.tile_size)) #(self.screen_rect.x, self.screen_rect.y))

	def eraser(self, Map): # Стирает объект на карте
		if type(self) == Wall: # Стена статична, не отрисовывать ее на карте каждый раз
			pass
		else:
			
			int_x = int(floor(self.x)) # int() - костыль для второго питона
			int_y = int(floor(self.y))
			
			if self.symbol in Map.get(int_x, int_y): # Ячейка x, y, в которой был персонаж
				Map.get(int_x, int_y)[Map.get(int_x, int_y).index(self.symbol)] = 0 # Сменить его символ на пустой

	def pencil(self, Map): # Рисует объект на карте
		
		int_x = int(floor(self.x)) # int() - костыль для второго питона
		int_y = int(floor(self.y))
		
		if type(self) == Wall:
			if not self.painted:
				Map.get(int_x, int_y)[Map.get(int_x, int_y).index(0)] = self.symbol
				self.painted = True # Стена отрисована
			else:
				pass
		
		else:
			if 0 in Map.get(int_x, int_y): # Ячейка x, y, в которую пришел персонаж
				Map.get(int_x, int_y)[Map.get(int_x, int_y).index(0)] = self.symbol # Сменить пустой символ на символ персонажа
			else: # Если в ячейке еще кто-то, а пустых мест нет
				Map.map[int_x][int_y].append(self.symbol) # Расширяем список этим персонажем


class Map:
	def __init__(self):
		self.map = [ [[0] for i in range(map_size)] for i in range(map_size) ]

	# Функция возвращает список обьектов в данной точке карты
	def get(self, x, y):
		return self.map[x][y]

	def collisions(self):
		for y in range(map_size):
			for x in range(map_size):
				if 1 and 6 in self.get(x,y):
					background = pygame.image.load("./resources/game_over.jpeg")


class Wall(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = 8):
		GameObject.__init__(self, './resources/wall.png', x, y, factor_tile, symbol)
		self.painted = False # Отрисована ли стена на карте

	def game_tick(self):
		self.tick += 1


class Ghost(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = 1):
		GameObject.__init__(self, './resources/ghost.png', x, y, factor_tile, symbol)
		self.direction = 0 # 0 - неподвижен, 1 - вправо, 2 - вниз, 3 - влево, 4 - вверх
		self.velocity = 1.0 / 2.0 # Скорость в клетках / игровой тик. Необходимо указывать дробную часть, иначе Питон интерпертирует это как целочисленное деление
		Ghosts.append(self)

	def game_tick(self):
		self.tick += 1
		if ITS_TEST: # Если тестовый режим запущен
			pass
		else:
			# Каждые 10 тиков случайно выбираем направление движения
			# Вариант self.direction == 0 соотвествует моменту первого вызова метода game_tick() у обьекта
			if self.tick % 10 == 0 or self.direction == 0:
				self.direction = random.randint(1, 4)
		# Для каждого направления движения увеличиваем координату до тех пор, пока не достигнем стены
		# Далее случайно меняем напрвление движения
			if self.direction == 1:
				self.x += self.velocity
				if self.x >= map_size-1:
					self.x = map_size-1
					self.direction = random.randint(1, 4)
			elif self.direction == 2:
				self.y += self.velocity
				if self.y >= map_size-1:
					self.y = map_size-1
					self.direction = random.randint(1, 4)
			elif self.direction == 3:
				self.x -= self.velocity
				if self.x <= 0:
					self.x = 0
					self.direction = random.randint(1, 4)
			elif self.direction == 4:
				self.y -= self.velocity
				if self.y <= 0:
					self.y = 0
					self.direction = random.randint(1, 4)

			self.set_coord(self.x, self.y)


class Pacman(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = 6):
		GameObject.__init__(self, './resources/pacman.png', x, y, factor_tile, symbol)
		self.direction = 0 # 0 - неподвижен, 1 - вправо, 2 - вниз, 3 - влево, 4 - вверх
		self.velocity = 1 / 1 # Скорость в клетках / игровой тик

	def game_tick(self):
		self.tick += 1
		if self.direction == 1:
			self.x += self.velocity
			if self.x >= map_size-1:
				self.x = map_size-1
		elif self.direction == 2:
			self.y += self.velocity
			if self.y >= map_size-1:
				self.y = map_size-1
		elif self.direction == 3:
			self.x -= self.velocity
			if self.x <= 0:
				self.x = 0
		elif self.direction == 4:
			self.y -= self.velocity
			if self.y <= 0:
				self.y = 0

		self.set_coord(self.x, self.y)

# Функция говорит, что делать при определенных событиях, сгенерированных пользователем
def process_events(events, packman):
	for event in events:
		# Если была нажата кнопка закрытия окна или клавиша Esc, то процесс завершается
		if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0)
		# Выставляем значение поля direction у Packman в зависимости от нажатой клавиши
		elif event.type == KEYDOWN:
			if event.key == K_LEFT:
				packman.direction = 3
			elif event.key == K_RIGHT:
				packman.direction = 1
			elif event.key == K_UP:
				packman.direction = 4
			elif event.key == K_DOWN:
				packman.direction = 2
			elif event.key == K_SPACE:
				packman.direction = 0
			
			elif event.key == K_t: # Запуск тестового режима
				test()


def test():
	global N
	global ITS_TEST

	if N % 2 != 0:
		ITS_TEST = False
		N += 1
	else:
		ITS_TEST = True
		N += 1


if __name__ == '__main__': # Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла без пути и расширения ('pacman'). Если файл запускается непосредственно, __name__  принимает значенние __main__
	init_window() # Инициализируем окно приложения
	ghost = Ghost(10, 15)
	pacman = Pacman(0, 0)
	wall = Wall(8, 8)

	background = pygame.image.load("./resources/background.png") # Загружаем изображение
	screen = pygame.display.get_surface() # Получаем объект Surface для рисования в окне
	# Засовывать это в init_window() нельзя: screen требуется для draw персонажей,
	# и сделать screen глобальным параметром, отделив тем самым от pygame.init(), тоже невозможно

	Map = Map()

# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), pacman)
		pygame.time.delay(50)
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей		
		for obj in Objects:
			obj.eraser(Map)
			obj.game_tick()
			obj.pencil(Map)
			obj.draw(screen)
		#Map.collisions()
		pygame.display.update()
		os.system('cls') # Очистить консоль
		for y in range(map_size):
			for x in range(map_size):
				print(Map.get(x,y), end = ' ')
			print()
		print(int(floor(pacman.x)),int(floor(pacman.y)))
		print("It's test =",ITS_TEST)

