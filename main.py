#!/usr/bin/env python

#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import time
import pygame
import sys
import math
import itertools
import json

class vec3:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def project(self, space):
        coords = (self.x, self.y, self.z)
        res = []
        for r in space:
            c = 0
            for sc, vc in zip(r, coords):
                c += (sc * vc)
            res.append(c)
        return res

def determ(mat):
    return (((mat[0][0]*mat[1][1]*mat[2][2])+(mat[0][1]*mat[1][2]*mat[2][0])+(mat[0][2]*mat[1][0]*mat[2][1])) -
            ((mat[0][2]*mat[1][1]*mat[2][0])+(mat[0][1]*mat[1][0]*mat[2][2])+(mat[0][0]*mat[1][2]*mat[2][1])))

def solve(sistema):
    A = [e[:3] for e in sistema]
    res = []
    detA = determ(A)
    for i in range(3):
        Ai = [[e[3] if n==i else e[n] for n in range(3)] for e in sistema]
        res.append(determ(Ai)/detA)
    return res

def transpose(mat):
    res = []
    for _ in range(len(mat[0])):
        res.append([])
    for r in mat:
        for n, e in enumerate(r):
            res[n].append(e)
    return res

def invert_mat(mat):
    res = []
    for i in range(len(mat)):
        sis = []
        for n,r in enumerate(mat):
            if n == i:
                sis.append(r + [1])
            else:
                sis.append(r + [0])
        res.append(solve(sis))
    return(transpose(res))

def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Monospace', 30)


    semispazi = [[-1, 0, 0, 1],
                 [ 1, 0, 0, 1],
                 [ 0,-1, 0, 1],
                 [ 0, 1, 0, 1],
                 [ 0, 0,-1, 1],
                 [ 0, 0, 1, 1],
                 [-1,-1,-1, 2]]

    """
    punti = [vec3(0,0,0),
             vec3(0,1,0)]

    segmenti = [(0,1)]
    """

    devochiudere = False

    screen = pygame.display.set_mode((960, 720))
    clock = pygame.time.Clock()

    step = False
    single = len(sys.argv) > 1 and (sys.argv[1] == 'step')

    longitudine_deg = 0
    latitudine_deg = 0
    rollio_deg = 0

    latitudine =  0
    longitudine = 0
    rollio = 0

    raggio = 0

    while not devochiudere:
        
        if (not single) or step:
            screen.fill('black')

            longitudine = longitudine_deg*math.pi/180
            latitudine = latitudine_deg*math.pi/180
            rollio = rollio_deg*math.pi/180

            lookvector = (-math.cos(latitudine)*math.sin(longitudine),-math.sin(latitudine),math.cos(latitudine)*math.cos(longitudine))

            punti_spaziati = []
            for sn in itertools.combinations(enumerate(semispazi), 3):
                sg = [a[:3] + [-a[3],] for a in [x[1] for x in sn]]
                if determ([s[:3] for s in sg]) == 0:
                    continue
                point = (solve(sg),[x[0] for x in sn])
                ammesso = True
                for s in semispazi:
                    if ((s[0]*point[0][0])+(s[1]*point[0][1])+(s[2]*point[0][2]))+s[3] < -(10**(-10)):
                        ammesso = False
                if ammesso:
                    punti_spaziati.append(point)

            segmenti_spaziati = []
            for n0, p0 in enumerate(punti_spaziati):
                for n1, p1 in list(enumerate(punti_spaziati))[n0:]:
                    n_com = 0
                    com = []
                    for s in p0[1]:
                        if s in p1[1]:
                            n_com += 1
                            com.append(s)
                    if n_com == 2:
                        segmenti_spaziati.append(((n0, n1),
                                         (com[0], com[1])))


            punti = [vec3(p[0][0],p[0][1],p[0][2]) for p in punti_spaziati]

            matrice_proiezione = [[math.cos(longitudine)                     , 0                   , math.sin(longitudine)],
                                  [math.sin(longitudine)*math.sin(latitudine),-math.cos(latitudine),-math.cos(longitudine)*math.sin(latitudine)]]

            proiettati = [p.project(matrice_proiezione) for p in punti]
            proiettati = [[(x*100)+(960/2), (y*100)+(720/2)] for x,y in proiettati]

            matrice_proiezione.append(list(lookvector))

            rev = invert_mat(matrice_proiezione)

            cut_vec = vec3(-math.cos(rollio), math.sin(rollio), 0).project(rev)

            cut_vec.append(raggio/100)
            
            segmenti = []
            for ss in segmenti_spaziati:
                visibile = False
                for s in ss[1]:
                    spazio = semispazi[s]
                    if (spazio[0]*lookvector[0])+(spazio[1]*lookvector[1])+(spazio[2]*lookvector[2]) >= 0:
                        visibile = True
                if visibile:
                    segmenti.append(ss[0])

            for s in segmenti:
                p0 = proiettati[s[0]]
                p1 = proiettati[s[1]]
                pygame.draw.line(screen, "yellow", p0, p1, width=3)

            pygame.draw.line(screen, "red", (raggio*math.cos(rollio) - 70*math.sin(rollio) + (960/2),-raggio*math.sin(rollio) - 70*math.cos(rollio) + (720/2)),
                                            (raggio*math.cos(rollio) + 70*math.sin(rollio) + (960/2),-raggio*math.sin(rollio) + 70*math.cos(rollio) + (720/2)))


            pygame.display.flip()
            
        step = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                devochiudere = True
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    step = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    longitudine_deg += 10
                    if longitudine_deg >= 360:
                        longitudine_deg -= 360
                elif event.key == pygame.K_LEFT:
                    longitudine_deg -= 10
                    if longitudine_deg < 0:
                        longitudine_deg += 360
                elif event.key == pygame.K_UP:
                    latitudine_deg += 10
                    if latitudine_deg >= 360:
                        latitudine_deg -= 360
                elif event.key == pygame.K_DOWN:
                    latitudine_deg -= 10
                    if latitudine_deg < 0:
                        latitudine_deg += 360
                elif event.key == pygame.K_z:
                    rollio_deg += 10
                    if rollio_deg >= 360:
                        rollio_deg -= 360
                elif event.key == pygame.K_c:
                    rollio_deg -= 10
                    if rollio_deg < 0:
                        rollio_deg += 360
                elif event.key == pygame.K_s:
                    raggio += 10
                elif event.key == pygame.K_x:
                    raggio -= 10
                elif event.key == pygame.K_SPACE:
                    semispazi.append(cut_vec)
                elif event.key == pygame.K_q:
                    f = open("modello.json", "w")
                    json.dump(semispazi, f)
                    f.close()
                    devochiudere = True
                elif event.key == pygame.K_l:
                    f = open("modello.json", "r")
                    semispazi = json.load(f)
                    f.close()

                    


        clock.tick(30)


    pygame.quit()

if __name__ == "__main__":
    main()
