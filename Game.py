import pygame
import neat
import time
import random
import os

WIN_WIDTH= 800
WIN_HEIGHT=600


CAR_IMG = pygame.image.load(os.path.join("imgs","car.png"))
CAR_IMGS = [pygame.image.load(os.path.join("imgs","car0.png")),pygame.image.load(os.path.join("imgs","car1.png")),pygame.image.load(os.path.join("imgs","car2.png")),
            pygame.image.load(os.path.join("imgs","car3.png")),pygame.image.load(os.path.join("imgs","car4.png")),pygame.image.load(os.path.join("imgs","bus1.png")),
            pygame.image.load(os.path.join("imgs","bus2.png")),pygame.image.load(os.path.join("imgs","ambulance.png")),pygame.image.load(os.path.join("imgs","car_crash.png"))]
CAR_CRASH_IMGS = [pygame.image.load(os.path.join("imgs","car_crash0.png")),pygame.image.load(os.path.join("imgs","car_crash1.png")),pygame.image.load(os.path.join("imgs","car_crash2.png"))]

BACKGROUND_IMG = pygame.image.load(os.path.join("imgs","background.png"))

class Car:
    IMGS=CAR_IMG
    MAX_ROTATION=5
    ROT_VEL=10
    ANIMATION_TIME=5
    
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 10
        self.height = self.y
        self.img_count = 0
        self.count = 0
      
        self.img = self.IMGS
      

    def up(self):
        if self.y<=60:
            self.y=60

        self.y -= self.vel
        
        self.tilt = self.MAX_ROTATION  # Tilt up
        self.count = 0

    def down(self):
        if self.y>=400:
            self.y=400
        self.y += self.vel
        self.tilt = -self.MAX_ROTATION  # Tilt down
        self.count = 0

    def draw(self, win):
      
        self.count +=1 


     
        if self.count > 5:
            self.tilt = 0
            
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)


    def get_mask(self):
        return pygame.mask.from_surface(self.img);

class Background:
    VEL = 10
    WIDTH = BACKGROUND_IMG.get_width()
    IMG = BACKGROUND_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self,win):
        win.blit(self.IMG,(self.x1, self.y))
        win.blit(self.IMG,(self.x2, self.y))


class obstacle:
    VEL = 11
    options = [230, 400, 60]
    
    def __init__(self):
        
        self.x = 800
        self.x2 = 800
        self.topdanger = 230
        self.botdanger = 230+142
        
        self.passed = False
        self.IMG1_index = random.randint(0, len(CAR_IMGS) - 1)
       
        self.IMG2_index = random.randint(0, len(CAR_IMGS) - 1)
        self.IMG1=pygame.transform.flip(CAR_IMGS[self.IMG1_index], True, True)
        self.IMG2=pygame.transform.flip(CAR_IMGS[self.IMG2_index], True, True)
        self.num_cars = random.randint(1, 2)
        self.img_count=0
        self.car_y = [0,0]
        self.set()
       
    def move(self):
        
        self.x -=self.VEL
        if self.IMG1_index>=len(CAR_IMGS) - 4 or self.IMG2_index>=len(CAR_IMGS) - 4:
            self.x2-=10

    def set(self):
        random.shuffle(self.options)
    
        
        
        self.car_y[0]=self.options[0]
        if self.num_cars == 2:
            self.car_y[1]=self.options[1]

        self.topdanger=self.options[2]-10
        self.botdanger=self.options[2]+140

       
    def spawn(self,win):
     
        self.img_count += 1

        if self.IMG1_index >= len(CAR_IMGS) - 1:
            if self.img_count < 5:
                img = CAR_CRASH_IMGS[0]  
            elif self.img_count < 10:
                img = CAR_CRASH_IMGS[1]  
            elif self.img_count < 15:
                img = CAR_CRASH_IMGS[2] 
            else:
                img = CAR_CRASH_IMGS[0]   
                self.img_count = 0  

            win.blit(pygame.transform.flip(img, True, True), (self.x2, self.car_y[0]))

        else:
            win.blit(self.IMG1, (self.x, self.car_y[0]))

        if self.num_cars == 2:
            if self.IMG2_index >= len(CAR_IMGS) - 1:
                if self.img_count < 5:
                    img = CAR_CRASH_IMGS[0]  
                elif self.img_count < 10:
                    img = CAR_CRASH_IMGS[1]  
                elif self.img_count < 15:
                    img = CAR_CRASH_IMGS[2]  
                else:
                    img = CAR_CRASH_IMGS[0]  
                    self.img_count = 0 

                win.blit(pygame.transform.flip(img, True, True), (self.x2, self.car_y[1]))

            else:
                win.blit(self.IMG2, (self.x, self.car_y[1]))
        
        start_pos = (780, self.topdanger) 
        end_pos = (780, self.botdanger)
        pygame.draw.line(win, (255, 0, 0), start_pos, end_pos, 5)

        

    def collide(self, car):
        car_mask = car.get_mask()  
        obstacle_mask1 = pygame.mask.from_surface(self.IMG1)
        obstacle_mask2 = pygame.mask.from_surface(self.IMG2)

        top_offset = (self.x - car.x, self.car_y[0] - car.y) 
        top_col_point = car_mask.overlap(obstacle_mask1, top_offset)

        if self.num_cars > 1:
            bottom_offset = (self.x - car.x, self.car_y[1] - car.y)  
            bot_col_point = car_mask.overlap(obstacle_mask2, bottom_offset)
            return top_col_point or bot_col_point
        else:
            return top_col_point

        
class Light:
    VEL = 10   
    def __init__(self):
        self.radius = 200
        self.x1 = 0
        self.x2 = WIN_WIDTH+300  
        self.color = (10,10,10)
        self.create_light_circle()
        

    def darken_screen(self,screen, darkness):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT)) 
        overlay.set_alpha(darkness)  
        overlay.fill((0, 0, 0))  
        screen.blit(overlay, (0, 0))  


    def create_light_circle(self):
        self.light_circle_surface = pygame.Surface((self.radius * 2, self.radius * 2))
       
        pygame.draw.circle(self.light_circle_surface, self.color, (self.radius, self.radius), self.radius)
        self.light_circle_surface.set_colorkey((0,0,0))
                  
    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL

        if self.x1 + self.radius*2 < 0:
            self.x1 = self.x2 + WIN_WIDTH+300   

        if self.x2 + self.radius*2 < 0:
            self.x2 = self.x1 + WIN_WIDTH+300  

    def draw_light(self,win):
        win.blit(self.light_circle_surface, (self.x1-self.radius , 300-self.radius), special_flags=pygame.BLEND_RGB_ADD)
        win.blit(self.light_circle_surface, (self.x2-self.radius , 300-self.radius), special_flags=pygame.BLEND_RGB_ADD)


def draw_win(win,cars,obs,background,font,score,light):
   
   
     
   
    background.draw(win)
    for car in cars:
        car.draw(win)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    win.blit(score_text, (10, 10))
    
    for ob in obs:
        ob.spawn(win)
    

    light.darken_screen(win,100)
    light.draw_light(win)
    
   
    pygame.display.update()



def main(genomes,config):
    pygame.init()
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Tunnel drive")

    
    cars = []
    nets = []
    ge = []


    for  genome_id,genome in genomes:
        genome.fitness = 0  
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.append(Car(10,230))
        ge.append(genome)   

    clock = pygame.time.Clock()
    light = Light()
    
    obs = [obstacle()]
    background = Background(0)
    font = pygame.font.SysFont(None, 36)
    
    score = 0
    run = True
    
    while run:
        clock.tick(30)
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()     
        
        
       
        ob_ind = 0
        if len(cars) > 0:
            if len(obs) > 1 and cars[0].x > obs[0].x + obs[0].IMG1.get_width():  
                ob_ind = 1                                                           
        else:
            run = False
            break
        for x,car in enumerate(cars):
            
           
            ge[x].fitness +=0.1
            
          
            output = nets[x].activate((car.y,abs(car.y - obs[ob_ind].topdanger),abs(car.y - obs[ob_ind].botdanger)))

           
            if output[0] > 0.5:  
                car.up()
            elif output[1] > 0.5:  
                car.down()



        delete = []
        add_obstacle = False

        for ob in obs :
            for x,car in enumerate(cars):
                if ob.collide(car):
                    ge[x].fitness -= 2 
                    cars.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                    
           
                if not ob.passed and ob.x < car.x :
                    ob.passed = True
                    add_obstacle = True

            if ob.x + ob.IMG1.get_width() < 0 :
                delete.append(ob)
                
            ob.move()

        if add_obstacle:
            score += 1
            for g in ge:
                g.fitness += 1
            obs.append(obstacle())

        for d in delete:
            obs.remove(d)

        if score>50:
            run = False
            break

        background.move()
        light.move()
        draw_win(win,cars,obs,background,font,score,light)
        



class BestGenomeReporter(neat.reporting.BaseReporter):
    def __init__(self):
        pass

    def post_evaluate(self, config, population, species, best_genome):
        # This method is called automatically by NEAT after each generation
        # 'best_genome' is the genome with the highest fitness in the current generation
        print('\nBest genome of current generation:\n{!s}'.format(best_genome))     

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(BestGenomeReporter())
    

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    
    
   
if __name__ == "__main__":
   # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    run(config_path)
