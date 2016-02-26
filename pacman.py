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
OBJECTS = []
GHOSTS = []
ITS_TEST = False
N = 0 # Кол-во запусков тестового режима
empty_symbol = ' ' # Символ, которым заполняется карта в пустых ячейках

def init_window():
	pygame.init() # Инициализируем библиотеку - чтоа?
	pygame.display.set_mode((512, 512)) # Задаем размеры окна
	pygame.display.set_caption('Pacman by Alex') # Задаем загаловок окна


def draw_background(scr, img = None):
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
		OBJECTS.append(self)
		self.x = x
		self.y = y

	def draw(self, scr):
		scr.blit(self.image, (floor(self.x) * self.tile_size, floor(self.y) * self.tile_size)) #(self.screen_rect.x, self.screen_rect.y))

	def eraser(self, Map): # Стирает объект на карте
		if type(self) == Wall: # Стена статична, не отрисовывать ее на карте каждый раз
			pass

		else:
			
			int_x = int(floor(self.x)) # int() - костыль для второго питона
			int_y = int(floor(self.y))
			tile = Map.get(int_x, int_y) # Ячейка x, y, в которой был персонаж

			tile.remove(self.symbol)

	def pencil(self, Map): # Рисует объект на карте
		int_x = int(floor(self.x)) # int() - костыль для второго питона
		int_y = int(floor(self.y))

		tile = Map.get(int_x, int_y) # Ячейка x, y, в которую пришел персонаж
		
		if type(self) == Wall:
			pass
		
		else:
			if empty_symbol in tile:
				tile[0] = self.symbol # Сменить пустой символ на символ персонажа
			else:
				tile.append(self.symbol) # Расширяем список этим персонажем


class Map:
	def __init__(self, map_file = None):
		self.map = [ [[] for y in range(map_size)] for x in range(map_size) ]
		if map_file:
			strings = map_file.readlines()
			for string in strings:
				string.rstrip()
			for y in range(map_size):
				for x in range(map_size):
					self.map[x][y].append(strings[y][x])

	# Функция возвращает список обьектов в данной точке карты
	def get(self, x, y):
		return self.map[x][y]
	
	# Обрабатывает столкновения
	'''Увы, такой подход допускает в редких случаях прохождение двигающихся объектов сквозь друг друга, 
	но избегает гамовера на границе тайлов (когда призрак и пэкмен стоят не в одной ячейке)'''
	def collisions(self, obj_1, obj_2):
		for y in range(map_size):
			for x in range(map_size):
				tile = self.get(x,y)
				if obj_1.symbol in tile:
					if obj_2.symbol in tile: # Конструкция obj_1.symbol and obj_2.symbol не работает

						# Столкновение со стеной
						if type(obj_2) == Wall:
							obj_1.eraser(self)
							if obj_1.direction == 1:
								obj_1.x = floor(obj_1.x) - 1
								obj_1.direction = 0
							elif obj_1.direction == 2:
								obj_1.y = floor(obj_1.y) - 1
								obj_1.direction = 0
							elif obj_1.direction == 3:
								obj_1.x = floor(obj_1.x) + 1
								obj_1.direction = 0
							elif obj_1.direction == 4:
								obj_1.y = floor(obj_1.y) + 1
								obj_1.direction = 0
							obj_1.pencil(self)
						# Столкновение Пэкмена и призрака 
						elif type(obj_1) == Pacman and type(obj_2) == Ghost or type(obj_2) == Pacman and type(obj_1) == Ghost:
							return True

	def direction(self, ghost, target):
		if ghost.x == target.x:
			if target.y > ghost.y:
				ghost.direction = 2
			else:
				ghost.direction = 4
		elif ghost.y == target.y:
			if target.x > ghost.x:
				ghost.direction = 1
			else:
				ghost.direction = 3
						


class Wall(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = '#'):
		GameObject.__init__(self, './resources/wall.png', x, y, factor_tile, symbol)
		self.painted = False # Отрисована ли стена на карте

	def game_tick(self):
		self.tick += 1


class Ghost(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = 'G'):
		GameObject.__init__(self, './resources/ghost_right.png', x, y, factor_tile, symbol)
		self.direction = 0 # 0 - неподвижен, 1 - вправо, 2 - вниз, 3 - влево, 4 - вверх
		self.velocity = 1.0 / 1.0 # Скорость в клетках / игровой тик. Необходимо указывать дробную часть, иначе Питон интерпертирует это как целочисленное деление
		GHOSTS.append(self)

	def game_tick(self):
		self.tick += 1
		if ITS_TEST: # Если тестовый режим запущен
			pass
		else:
			# Каждые 20 тиков случайно выбираем направление движения
			# self.direction == 0 соотвествует моменту первого вызова метода game_tick() у обьекта
			#if self.tick % 10 == 0 or self.direction == 0:
				#self.direction = random.randint(1, 4)
		# Для каждого направления движения увеличиваем координату до тех пор, пока не достигнем стены
		# Далее случайно меняем напрвление движения
			if self.direction == 1:
				self.x += self.velocity
				self.image = pygame.image.load('./resources/ghost_right.png')
				if self.x > map_size-1:
					self.x = map_size-1
					self.direction = random.randint(1, 4)
			elif self.direction == 2:
				self.y += self.velocity
				self.image = pygame.image.load('./resources/ghost_down.png')
				if self.y > map_size-1:
					self.y = map_size-1
					self.direction = random.randint(1, 4)
			elif self.direction == 3:
				self.x -= self.velocity
				self.image = pygame.image.load('./resources/ghost_left.png')
				if self.x < 0:
					self.x = 0
					self.direction = random.randint(1, 4)
			elif self.direction == 4:
				self.y -= self.velocity
				self.image = pygame.image.load('./resources/ghost_up.png')
				if self.y < 0:
					self.y = 0
					self.direction = random.randint(1, 4)


class Pacman(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = 'P'):
		GameObject.__init__(self, './resources/pacman_right.png', x, y, factor_tile, symbol)
		self.direction = 0 # 0 - неподвижен, 1 - вправо, 2 - вниз, 3 - влево, 4 - вверх
		self.velocity = 4.0 / 5.0 # Скорость в клетках / игровой тик

	def game_tick(self):
		self.tick += 1
		if self.direction == 1:
			self.x += self.velocity
			self.image = pygame.image.load('./resources/pacman_right.png')
			if self.x > map_size-1:
				self.x = map_size-1
		elif self.direction == 2:
			self.y += self.velocity
			self.image = pygame.image.load('./resources/pacman_down.png')
			if self.y > map_size-1:
				self.y = map_size-1
		elif self.direction == 3:
			self.x -= self.velocity
			self.image = pygame.image.load('./resources/pacman_left.png')
			if self.x < 0:
				self.x = 0
		elif self.direction == 4:
			self.y -= self.velocity
			self.image = pygame.image.load('./resources/pacman_up.png')
			if self.y < 0:
				self.y = 0


# Функция говорит, что делать при определенных событиях, сгенерированных пользователем
def process_events(events, control_obj):
	for event in events:
		# Если была нажата кнопка закрытия окна или клавиша Esc, то процесс завершается
		if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0)

		elif event.type == KEYDOWN:

			# Выставляем значение поля direction у Pacman в зависимости от нажатой клавиши
			if event.key == K_LEFT:
				control_obj.direction = 3
			elif event.key == K_RIGHT:
				control_obj.direction = 1
			elif event.key == K_UP:
				control_obj.direction = 4
			elif event.key == K_DOWN:
				control_obj.direction = 2
			elif event.key == K_SPACE:
				control_obj.direction = 0

			# Запуск тестового режима
			elif event.key == K_t:
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


def main():
	global OBJECTS
	global GHOSTS
	#map_name = input()
	map_file = open('maps/1.txt')
	CHARACTERS = []

	background = pygame.image.load("./resources/background.png") # Загружаем изображение
	screen = pygame.display.get_surface() # Получаем объект Surface для рисования в окне
	# Засовывать это в init_window() нельзя: screen требуется для draw персонажей,
	# и сделать screen глобальным параметром, отделив тем самым от pygame.init(), тоже невозможно

	map = Map(map_file)
	map_file.close()
	for y in range(map_size):
		for x in range(map_size):
			tile = map.get(x,y)
			if '#' in tile:
				wall = Wall(x, y)
			elif 'G' in tile:
				ghost = Ghost(x, y)
			elif 'P' in tile:
				pacman = Pacman(x, y)
	exit_flag = False
	continue_flag = True
	CHARACTERS.append(pacman)
	CHARACTERS += GHOSTS

# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), pacman)
		for ghost in GHOSTS:
			map.direction(ghost, pacman)
		
		pygame.time.delay(50)
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей		

		for char in CHARACTERS:
			char.eraser(map)
			char.game_tick()
			char.pencil(map)

		# Обработка столкновений
		for char in CHARACTERS:
			for obj in OBJECTS:
				if map.collisions(char, obj) and continue_flag: # Если пэкмен столкнулся с призраком и событие не было зафиксировано
					exit_flag = True
					continue_flag = False # Событие зафиксировано, не повторять
				obj.draw(screen)
		pygame.display.update() # Без этого отрисованное не будет отображаться
		if exit_flag: # Произошло столкновение с призраком
			break
			
		'''os.system('cls') # Очистить консоль
		for y in range(map_size):
			for x in range(map_size):
				print(map.get(x,y), end = ' ')
			print()
		print("It's test =", ITS_TEST)'''

	background = pygame.image.load("./resources/game_over.png")
	draw_background(screen, background)
	pygame.display.update()
	OBJECTS = []
	GHOSTS = []
	pygame.time.delay(500)
	main() # Рестарт

if __name__ == '__main__': # Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла без пути и расширения ('pacman'). Если файл запускается непосредственно, __name__  принимает значенние __main__
	init_window() # Инициализируем окно приложения
	main()