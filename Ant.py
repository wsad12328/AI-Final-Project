import pygame
import sys

pygame.init()

# 设置窗口大小
width, height = 400, 300
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Three Circles with Different Transparency")

# 定义颜色
white = (255, 255, 255)
red = (255, 0, 0)

# 定义圆心和半径
center_x, center_y = width // 4, height // 2
radius = 50

# 定义不同透明度的圆的透明度值列表
alpha_values = [255, 128, 64]  # 可以根据需要调整透明度值

# 在循环中绘制不同透明度的圆
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 清屏
    screen.fill(white)

    # 绘制不同透明度的三个圆
    center_x = width // 4  # 重置圆心的X坐标
    for alpha_value in alpha_values:
        transparent_red = (red[0], red[1], red[2], alpha_value)
        pygame.draw.circle(screen, transparent_red, (center_x, center_y), radius)
        center_x += width // 4  # 将下一个圆的圆心位置调整一下，以便能够看到不同圆之间的差异

    # 刷新屏幕
    pygame.display.flip()

# 退出程序
pygame.quit()
sys.exit()
