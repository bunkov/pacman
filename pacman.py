import sys
import pygame
from pygame.locals import *
from math import floor
import random


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
	# img - путь к файлу с изображением персонажа
	# x, y - координаты персонажа на игровом поле
	# tile_size - размер клетки игрового поля в пикселях (предполагается, что клетки квадратные)
	# map_size - размер карты игрового поля в клетках (предполагается, что карта квадратная)
	def __init__(self, img, x, y, tile_size, map_size):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img) # Загружаем изображение персонажа
		self.tick = 0 # Время, прошедшее с момента создания персонажа, в условных единицах
		self.tile_size = tile_size
		self.map_size = map_size
		self.set_coord(x, y)

	def set_coord(self, x, y):
		self.x = x
		self.y = y
		self.screen_rect = Rect(floor(x) * self.tile_size, floor(y) * self.tile_size, self.tile_size, self.tile_size )
		# Переменная, хранящая размеры и координаты отрисовки персонажа на экране
		# !!! Вызвать здесь draw?

	def game_tick(self):
		self.tick += 1
	# Функция вызывается с каждым тиком игровых часов

	def draw(self, scr):
		scr.blit(self.image, (self.screen_rect.x, self.screen_rect.y))


class Ghost(GameObject):
	def __init__(self, x, y, tile_size, map_size):
		GameObject.__init__(self, './resources/ghost.png', x, y, tile_size, map_size)
		self.direction = 0 # 0 - неподвижен, 1 - вправо, 2 - вниз, 3 - влево, 4 - вверх
		self.velocity = 4.0 / 10.0 # Скорость в клетках / игровой тик

	def game_tick(self):
		super(Ghost, self).game_tick() # !!! Либо изменить tick напрямую, либо убрать этот атрибут
		# Каждые 20 тиков случайно выбираем направление движения
		# Вариант self.direction == 0 соотвествует моменту первого вызова метода game_tick() у обьекта
		if self.tick % 20 == 0 or self.direction == 0:
			self.direction = random.randint(1, 4)
	# Для каждого направления движения увеличиваем координату до тех пор, пока не достигнем стены
	# Далее случайно меняем напрвление движения
		if self.direction == 1:
			self.x += self.velocity
			if self.x >= self.map_size-1:
				self.x = self.map_size-1
				self.direction = random.randint(1, 4)
		elif self.direction == 2:
			self.y += self.velocity
			if self.y >= self.map_size-1:
				self.y = self.map_size-1
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
	def __init__(self, x, y, tile_size, map_size):
		GameObject.__init__(self, './resources/pacman.png', x, y, tile_size, map_size)
		self.direction = 0 # 0 - неподвижен, 1 - вправо, 2 - вниз, 3 - влево, 4 - вверх
		self.velocity = 4.0 / 10.0 # Скорость в клетках / игровой тик

	def game_tick(self):
		super(Pacman, self).game_tick() # !!! Либо изменить tick напрямую, либо убрать этот атрибут
		if self.direction == 1:
			self.x += self.velocity
			if self.x >= self.map_size-1:
				self.x = self.map_size-1
		elif self.direction == 2:
			self.y += self.velocity
			if self.y >= self.map_size-1:
				self.y = self.map_size-1
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


if __name__ == '__main__': # Если этот файл импортируется в другой, этот __name__ равен имени импортируемого файла без пути и расширения ('pacman'). Если файл запускается непосредственно, __name__  принимает значенние __main__
	init_window() # Инициализируем окно приложения

	tile_size = 32
	map_size = 16
	# !!! Объявить глобальными переменными и избавиться от избыточного описания объектов?

	ghost = Ghost(0, 0, tile_size, map_size)
	pacman = Pacman(5, 5, tile_size, map_size)

	background = pygame.image.load("./resources/background.png") # Загружаем изображение
	screen = pygame.display.get_surface() # Получаем объект Surface для рисования в окне
	# !!! Засунуть это в init_window()?

# В бесконечном цикле принимаем и обрабатываем сообщения
	while 1:
		process_events(pygame.event.get(), pacman)
		pygame.time.delay(100)
		ghost.game_tick()
		pacman.game_tick()
		draw_background(screen, background) # !!! Зачем отрисовывать фон каждый раз?
		pacman.draw(screen)
		ghost.draw(screen)
		pygame.display.update()

