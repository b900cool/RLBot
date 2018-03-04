import math
import time

class Agent:
    def __init__(self, name, team, index):

        #Index denotes the team that the bot is on, Blue or Orange
        #Orange = 1
        #Blue = 0
        self.index = index

        # Contants
        self.DODGE_TIME = 0.1
        self.DODGEDISTANCE = 400
        self.DISTANCETOBOOST = 1500
        self.DISTANCETOBOOSTHIT = 500
        self.POWERSLIDEANGLE = 150
        #used to turn the bot only if it is far enough behind the ball
        self.POSITIONINGOFFSET = 300

        self.MAXIMUM_DISTANCE_TO_CHASE_TARGET = 750

        

        # Controller inputs
        self.throttle = 0
        self.steer = 0.0
        self.pitch = 0
        self.yaw = 0
        self.roll = 0
        self.boost = False
        self.jump = False
        self.powerslide = False

        # Game values
        self.bot_pos = None
        self.bot_rot = None
        self.ball_pos = None
        self.bot_yaw = None

        self.distanceToBall = 0

        #half flip values
        self.shouldHalf = False
        self.secondHalf = False
        self.stallSeq = False
        #timers used to stall the halfflip at certain stages
        self.stallTimer1 = 0
        self.stallTimer2 = 0
        #constants used to define the stall timer delay
        self.HALFTIME = 0.3
        self.HALFTIME2 = 1
        self.startTimer = 3 + time.time()

        self.angle_between_bot_and_target = 0

        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0

    def angFrontToTarget(self, target_x, target_y):
        angle_between_bot_and_target = math.degrees(math.atan2(target_y - self.bot_pos.Y,
                                                            target_x - self.bot_pos.X))

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        if angle_front_to_target < -180:
            angle_front_to_target += 360
        if angle_front_to_target > 180:
            angle_front_to_target -= 360

        return angle_front_to_target

    #aims the bot towards the ball
    #will also cause the bot to powerslide if the angle between it and the ball is great enough
    def aim(self, target_x, target_y):

        angle_between_bot_and_target = math.degrees(math.atan2(target_y - self.bot_pos.Y,
                                                            target_x - self.bot_pos.X))

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        print(abs(angle_front_to_target))

        if angle_front_to_target < -180:
            angle_front_to_target += 360
        if angle_front_to_target > 180:
            angle_front_to_target -= 360

        angle_front_to_target
        # Correct the values
        

        if angle_front_to_target < -10:
            # If the target is more than 10 degrees left from the centre, steer right
            self.steer = -1
        elif angle_front_to_target > 10:
            # If the target is more than 10 degrees right from the centre, steer left
            self.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.steer = 0



        if (abs(angle_front_to_target)) > self.POWERSLIDEANGLE:
            self.powerslide = True
            self.boost = False
            
        else:
            self.powerslide = False

    #controls when the bot boosts
    def boostControl(self, target_x, target_y, distanceToBall):
        #distanceToBall = math.sqrt(math.pow(target_x-self.bot_pos.X, 2)+math.pow(target_y-self.bot_pos.Y, 2))
        #print(distanceToBall)
        if distanceToBall > self.DISTANCETOBOOST or (self.ball_pos.X == 0 and self.ball_pos.Y == 0) or distanceToBall < self.DISTANCETOBOOSTHIT:
            self.boost = True
        else:
            self.boost = False

    def throttleControl(self, distanceToBall):
        if distanceToBall > 1000:
            self.throttle = 1
        elif distanceToBall > 500:
            self.throttle = .75
        else:
            self.throttle = .5

    #checks to see if the bot can dodge at a given time
    def DodgeCheck(self, target_x, target_y):
        
        angle_front_to_target = self.angFrontToTarget(target_x, target_y)
        if angle_front_to_target < 15 and angle_front_to_target > -15:
            self.pitch = -1
        elif angle_front_to_target > 15 and angle_front_to_target < 45:
            self.pitch = -.71
            self.yaw = .71
        elif angle_front_to_target < -15 and angle_front_to_target > -45:
            self.pitch = -.71
            self.yaw = -.71
        elif angle_front_to_target > 45 and angle_front_to_target < 90:
            self.yaw = 1
        elif angle_front_to_target < -45 and angle_front_to_target > -90:
            self.yaw = 1


        if self.should_dodge and time.time() > self.next_dodge_time:
            self.aim(target_x, target_y)
            self.jump = True
            

            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME

    #calculates distance between the bot and the ball
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    #allows bot to boost on kickoff (Now a part of boostControl)
    #def kickoffBoost(self):
    #   if self.ball_pos.X == 0 and self.ball_pos.Y == 0:
    #      self.boost = True
    # else:
    #    self.boost = False

    #allows the bot to half flip!!!!!
    def HalfFlip(self):
        
        #checks that the half flip is being used and that the first jump has not already been made
        #when time.time() < next_dodge_time than the second flip can be done
        if self.shouldHalf and time.time() > self.next_dodge_time:
            self.jump = True
            self.pitch = 1
            #self.yaw = 0.63

            #code to perform the second flip and prepare timers 
            if self.secondHalf and not self.stallSeq:
                self.pitch = .87
                self.yaw = -.5
                self.stallSeq = True
                self.secondHalf = False
                self.stallTimer1 = time.time() + self.HALFTIME
            #executes the timer delay for the wheels to align with the ceiling
            elif self.stallTimer1 > time.time():
                self.stallTimer2 = time.time() + self.HALFTIME2
            #executes the timer delay to stall the flip
            elif self.stallTimer2 > time.time():
                self.pitch = -1
                self.yaw = 0
            else:
                self.secondHalf = True
                self.next_dodge_time = time.time() + self.DODGE_TIME
                if self.stallTimer2 < time.time():
                    self.stallSeq = False
                    self.shouldHalf = False
                    self.yaw = 0
                    self.pitch = 0

    def RightSelf(self, roll):
        if roll > 14000:
            self.roll = -1
        elif roll < -14000:
            self.roll = 1
        elif roll > 7000:
            self.roll = -.5
        elif roll < -7000:
            self.roll = .5
        elif roll > 3500:
            self.roll = -.25
        elif roll < -3500:
            self.roll = .25

    def closestPoint(self, x1, y1, x2, y2, x3, y3):
        k = ((y2 - y1) * (x3 - x1) - (x2 - x1) * (y3 - y1)) / ((y2 - y1) ** 2 + (x2 - x1) ** 2)
        x4 = x3 - k * (y2 - y1)
        y4 = y3 + k * (x2 - x1)

        return x4, y4

    def get_output_vector(self, values):
        # Update game data variables
        self.bot_pos = values.gamecars[self.index].Location
        self.bot_rot = values.gamecars[self.index].Rotation
        self.ball_pos = values.gameball.Location
        self.distanceToBall = self.distance(self.bot_pos.X, self.ball_pos.X, self.bot_pos.Y, self.ball_pos.Y)

    

        # Get car's yaw and convert from Unreal Rotator units to degrees
        self.bot_yaw = abs(self.bot_rot.Yaw) % 65536 / 65536 * 360
        if self.bot_rot.Yaw < 0:
            self.bot_yaw *= -1

        #default aim statement for each frame
        #self.aim(self.ball_pos.X, self.ball_pos.Y)
        

        self.throttleControl(self.distanceToBall)

        #bot will boost if far enough away from the ball
        self.boostControl(self.ball_pos.X, self.ball_pos.Y, self.distanceToBall)
        

        

       
        
        

        

        #bot will aim itself toward the ball only if it is behind it
        if(self.index == 0 and self.bot_pos.Y+self.POSITIONINGOFFSET < self.ball_pos.Y) or (self.index == 1 and self.bot_pos.Y-self.POSITIONINGOFFSET > self.ball_pos.Y):
            if self.index == 0:
                enemy_goal = 5000
            else:
                enemy_goal = -5000
            #self.aim(self.ball_pos.X, self.ball_pos.Y)
            #Bot will dodge toward the ball only if closer than 400 units
           
            
            target = self.closestPoint(0, enemy_goal, self.ball_pos.X, self.ball_pos.Y, self.bot_pos.X, self.bot_pos.Y)

            if self.distance(target[0], target[1], self.bot_pos.X, self.bot_pos.Y) > self.MAXIMUM_DISTANCE_TO_CHASE_TARGET:
                # Go to the target if far away enough
                self.aim(target[0], target[1])
                #print("Target")
            else:
                # Chase ball if close to ball
                self.aim(self.ball_pos.X, self.ball_pos.Y)
                #print("Ball")

        #bot will drive to goal if not behind the ball
        else:
            if self.index == 0:
                self.aim(0, -5000)
            else:
                self.aim(0, 5000)

        

        #If bot is in goal it will reposition to the front of the goal
        if(self.index == 0 and self.bot_pos.Y < -5000) or (self.index == 1 and self.bot_pos.Y > 5000):
            if self.index == 0:
                self.aim(0, -5000)
            elif self.index == 1:
                self.aim(0, 5000)

        #self.jump = False
        #print (self.should_dodge)


        #this should be present once per frame before all jump check. Will ensure that there is a button release that triggers jump action
        self.jump = False
        #bot will dodge if close enough
        self.DodgeCheck(self.ball_pos.X, self.ball_pos.Y)
        if time.time() > self.startTimer and time.time() < self.startTimer + .1:
            self.shouldHalf = True
        
        if self.bot_pos.Z > 200:
            self.RightSelf(self.bot_rot.Roll)

        
        self.HalfFlip()
        
        






        return [self.throttle, self.steer,
                self.pitch, self.yaw, self.roll,
                self.jump, self.boost, self.powerslide]


    

