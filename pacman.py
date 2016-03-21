# -*- coding: utf-8 -*-
from __future__ import print_function
# костыли для второго питона

import sys
import pygame
from pygame.locals import *
import random
import os


tile_size = 32 # Размер клетки игрового поля в пикселях (предполагается, что клетки квадратные)
map_size = 16 # Размер карты игрового поля в клетках (предполагается, что карта квадратная)
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
		self.tile_size = tile_size * int(factor_tile)
		self.symbol = symbol
		self.x = x
		self.y = y

	def draw(self, scr):
		scr.blit(self.image, (int(self.x) * self.tile_size, int(self.y) * self.tile_size)) #(self.screen_rect.x, self.screen_rect.y))


class Map:
	def __init__(self, OBJECTS, CHARACTERS, POINTS, GHOSTS, map_file = None):
		self.map = [ [[] for y in range(map_size)] for x in range(map_size) ]
		if map_file:
			strings = map_file.readlines()
			for string in strings:
				string.rstrip()
			for y in range(map_size):
				for x in range(map_size):
					if strings[y][x] == '#':
						object = Wall(x, y)
						OBJECTS.append(object)
					elif strings[y][x] == 'G':
						object = Ghost(x, y)
						GHOSTS.append(object)
					elif strings[y][x] == 'P':
						object = Pacman(x, y)
						CHARACTERS.append(object)
					elif strings[y][x] == 'o':
						object = Point(x,y)
						POINTS.append(object)
					elif strings[y][x] == ' ':
						object = '<Пустой объект, серьезно!>'
					self.map[x][y].append(object)

	# Функция возвращает список обьектов в данной точке карты
	def get(self, x, y):
		return self.map[x][y]
	
	# Обрабатывает столкновения
	'''Увы, такой подход допускает в редких случаях прохождение двигающихся объектов сквозь друг друга, 
	но избегает гамовера на границе тайлов (когда призрак и пэкмен стоят не в одной ячейке)'''
	def collisions(self, obj_1, obj_2, OBJECTS, POINTS):
		int_x = int(obj_1.x)
		int_y = int(obj_1.y)
		tile = self.get(int_x,int_y)
		if obj_1 in tile:
			if obj_2 in tile: # Конструкция obj_1 and obj_2 не работает

				# Столкновение со стеной
				if type(obj_2) == Wall:
					if obj_1.direction == 1:
						obj_1.x = int_x - 1
						obj_1.direction = 0
					elif obj_1.direction == 2:
						obj_1.y = int_y - 1
						obj_1.direction = 0
					elif obj_1.direction == 3:
						obj_1.x = int_x + 1
						obj_1.direction = 0
					elif obj_1.direction == 4:
						obj_1.y = int_y + 1
						obj_1.direction = 0
					new_x = int(obj_1.x)
					new_y = int(obj_1.y)
					new_tile = self.get(new_x,new_y)
					new_tile.append(obj_1)
					tile.remove(obj_1)
				# Столкновение Пэкмена и призрака
				elif type(obj_1) == Pacman and type(obj_2) == Ghost or type(obj_2) == Pacman and type(obj_1) == Ghost:
					return True
				# Пэкмен съедает точку
				elif type(obj_1) == Pacman and type(obj_2) == Point:
					print('collisions',tile,obj_2.x,obj_2.y)
					tile.remove(obj_2)
					POINTS.remove(obj_2)
					OBJECTS.remove(obj_2)

		if  not POINTS: # Точек не осталось, массив пустой
			return True

	def direction(self, ghost, footprint_x, footprint_y):
		free_way = True
		# Если призрак на следе, продолжать движение и не менять его направление по-рандому
		if int(ghost.x) == footprint_x and int(ghost.y) == footprint_y:
			pass
		# Цель на линии призрака
		elif int(ghost.x) == footprint_x:
			# Проверка на наличие стен
			lower_edge = int(min(ghost.y, footprint_y))
			higher_edge = int(max(ghost.y, footprint_y))
			for y in range(lower_edge, higher_edge):
				tile = self.get(footprint_x, y)
				for obj in tile:
					if type(obj) == Wall:
						free_way = False
			
			if footprint_y > ghost.y and free_way:
				ghost.direction = 2
			elif footprint_y < ghost.y and free_way: # Нельзя допускать равенства, иначе призрак повернет в обратном направлении из-за того, что двигается по следу
				ghost.direction = 4
		
		elif int(ghost.y) == footprint_y:

			lower_edge = int(min(ghost.x, footprint_x))
			higher_edge = int(max(ghost.x, footprint_x))
			for x in range(lower_edge, higher_edge):
				tile = self.get(x, footprint_y)
				for obj in tile:
					if type(obj) == Wall:
						free_way = False
			
			if footprint_x > ghost.x and free_way:
				ghost.direction = 1
			elif footprint_x < ghost.x and free_way:
				ghost.direction = 3
		# Когда призрак попал в стену или только создан
		elif ghost.direction == 0:
			ghost.direction = random.randint(1, 4)
						


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
		self.velocity = 8.0 / 10.0 # Скорость в клетках / игровой тик. Необходимо указывать дробную часть, иначе Питон интерпертирует это как целочисленное деление

	def game_tick(self):
		self.tick += 1
		if ITS_TEST: # Если тестовый режим запущен
			pass
		else:
		# Для каждого направления движения увеличиваем координату до тех пор, пока не достигнем стены
		# Далее случайно меняем напрвление движения
			if self.direction == 1:
				self.x += self.velocity
				self.image = pygame.image.load('./resources/ghost_right.png')
				if self.x > map_size-1:
					self.x = map_size-1
			elif self.direction == 2:
				self.y += self.velocity
				self.image = pygame.image.load('./resources/ghost_down.png')
				if self.y > map_size-1:
					self.y = map_size-1
			elif self.direction == 3:
				self.x -= self.velocity
				self.image = pygame.image.load('./resources/ghost_left.png')
				if self.x < 0:
					self.x = 0
			elif self.direction == 4:
				self.y -= self.velocity
				self.image = pygame.image.load('./resources/ghost_up.png')
				if self.y < 0:
					self.y = 0


class Pacman(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = 'P'):
		GameObject.__init__(self, './resources/pacman_right.png', x, y, factor_tile, symbol)
		self.direction = 0 # 0 - неподвижен, 1 - вправо, 2 - вниз, 3 - влево, 4 - вверх
		self.velocity = 6.0 / 10.0 # Скорость в клетках / игровой тик

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

class Point(GameObject):
	def __init__(self, x, y, factor_tile = 1, symbol = 'o'):
		GameObject.__init__(self, './resources/point.png', x, y, factor_tile, symbol)

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
	OBJECTS = []
	GHOSTS = []
	POINTS = []
	CHARACTERS = []
	#map_name = input()
	map_file = open('maps/2.txt')

	background = pygame.image.load("./resources/background.png") # Загружаем изображение
	screen = pygame.display.get_surface() # Получаем объект Surface для рисования в окне
	# Засовывать это в init_window() нельзя: screen требуется для draw персонажей,
	# и сделать screen глобальным параметром, отделив тем самым от pygame.init(), тоже невозможно

	map = Map(OBJECTS, CHARACTERS, POINTS, GHOSTS, map_file)
	map_file.close

	exit_flag = False
	game_over_flag = False
	continue_flag = True
	pacman = CHARACTERS[0]
	CHARACTERS += GHOSTS
	OBJECTS += CHARACTERS + POINTS

# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), pacman)
		footprint_x = int(pacman.x)
		footprint_y = int(pacman.y)

		pygame.time.delay(100)
		draw_background(screen, background) # Фон перерисовывается поверх устаревших положений персонажей		

		for char in CHARACTERS:
			int_x = int(char.x)
			int_y = int(char.y)
			tile = map.get(int_x,int_y)
			if type(char) == Pacman:
				print(char.x,char.y)
			char.game_tick()
			
			new_x = int(char.x)
			new_y = int(char.y)
			new_tile = map.get(new_x,new_y)
			new_tile.append(char)
			tile.remove(char)

		# Обработка столкновений
		for char in CHARACTERS:
			for obj in OBJECTS:
				if map.collisions(char, obj, OBJECTS, POINTS) and continue_flag: # Если пэкмен столкнулся с призраком или собрал все точки, и событие не было зафиксировано
					exit_flag = True
					continue_flag = False # Событие зафиксировано, не повторять
					if type(obj) == Pacman and type(char) == Ghost or type(char) == Pacman and type(obj) == Ghost:
						game_over_flag = True
				obj.draw(screen)
		pygame.display.update() # Без этого отрисованное не будет отображаться
		if exit_flag: # Произошло столкновение с призраком
			print(POINTS, bool(POINTS))
			break
		
		for ghost in GHOSTS:
			map.direction(ghost, footprint_x, footprint_y)
			
		'''os.system('cls') # Очистить консоль
		for y in range(map_size):
			for x in range(map_size):
				print(map.get(x,y), end = ' ')
			print()
		print("It's Test =", ITS_TEST, POINTS)'''

	if game_over_flag:
		background = pygame.image.load("./resources/game_over.png")
	else:
		background = pygame.image.load("./resources/you.png")
		draw_background(screen, background)
		pygame.display.update()
		pygame.time.delay(500)
		background = pygame.image.load("./resources/win.png")
	draw_background(screen, background)
	pygame.display.update()
	OBJECTS = []
	GHOSTS = []
	POINTS = []
	pygame.time.delay(500)
	main() # Рестарт

if __name__ == '__main__': # Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла без пути и расширения ('pacman'). Если файл запускается непосредственно, __name__  принимает значенние __main__
	init_window() # Инициализируем окно приложения
	main()
