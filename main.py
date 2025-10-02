#!/usr/bin/env python

#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import time
import pygame
import sys
import math
import itertools
import json
import numpy as np

colori = [
        "white",
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "violet"
        ]

def genera_punti(spazi):
    punti = np.empty((0,3))
    spazi_associati = np.empty((0,3),dtype=np.uint32)
    for sn in itertools.combinations(enumerate(spazi), 3):
        S = np.array([x[1] for x in sn])
        A = np.delete(S,3,axis=1)
        B = -np.delete(S,[0,1,2], axis=1)
        if np.linalg.det(A) == 0:
            continue
        point = np.linalg.solve(A,B).transpose()
        ammesso = True
        for s in spazi:
            if np.dot(np.append(point,1), s) < -(10**(-10)):
                ammesso = False
        if ammesso:
            nn = np.array([x[0] for x in sn])
            punti = np.append(punti, point, axis=0)
            spazi_associati = np.append(spazi_associati, [nn], axis = 0)
    return (punti, spazi_associati)

def genera_segmenti(punti_spaziati):
    segmenti_spaziati = []
    punti, spazi = punti_spaziati
    for n0, p0 in enumerate(punti):
        for n1, p1 in list(enumerate(punti))[n0:]:
            n_com = 0
            com = []
            for s in spazi[n0]:
                if s in spazi[n1]:
                    n_com += 1
                    com.append(s)
            if n_com == 2:
                segmenti_spaziati.append( (n0, n1, int(com[0]), int(com[1])))
    return segmenti_spaziati

def stampa_tasselli(tasselli, rotazione, zoom, offset):
    A4 = (595, 842)
    f = open("output.ps", 'w')
    f.write("%!PS\n")
    f.write(f"<< /PageSize [{A4[0]} {A4[1]}] >> setpagedevice\n")
    f.write("0 0 0 setcolor\n")

    for t in tasselli:
        for s in t['lati']:
            a = (np.dot(rotazione,s[0]*100*zoom)+offset)*842/1000
            b = (np.dot(rotazione,s[1]*100*zoom)+offset)*842/1000
            f.write(f"{a[0]} {a[1]} moveto\n")
            f.write(f"{b[0]} {b[1]} lineto\n")
            f.write("2 setlinewidth\n")
            f.write("stroke\n")

    f.write("showpage\n")
    f.close()




def sculpt():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Monospace', 30)


    semispazi = np.array([[-1, 0, 0, 1],
                 [ 1, 0, 0, 1],
                 [ 0,-1, 0, 1],
                 [ 0, 1, 0, 1],
                 [ 0, 0,-1, 1],
                 [ 0, 0, 1, 1],
                 [-1,-1,-1, 2]])

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

            lookvector = np.array((-math.cos(latitudine)*math.sin(longitudine),-math.sin(latitudine),math.cos(latitudine)*math.cos(longitudine)))

            punti_spaziati = genera_punti(semispazi)

            segmenti_spaziati = genera_segmenti(punti_spaziati)

            punti = punti_spaziati[0]

            matrice_proiezione = np.array([[math.cos(longitudine)                     , 0                   , math.sin(longitudine)],
                                           [math.sin(longitudine)*math.sin(latitudine),-math.cos(latitudine),-math.cos(longitudine)*math.sin(latitudine)]])

            proiettati = np.dot(matrice_proiezione, punti.transpose()).transpose()
            proiettati = (proiettati*100)+ np.dot(np.ones((proiettati.shape[0], 1)), np.array([[960/2,720/2]]))

            nuova_matrice = np.append(matrice_proiezione, [lookvector], axis = 0)

            rev = np.linalg.inv(nuova_matrice)

            cut_vec = np.dot(rev, np.transpose(np.array((-math.cos(rollio), math.sin(rollio), 0))))
            

            cut_vec = np.append(cut_vec, raggio/100)
            
            segmenti = np.empty((0,2),dtype=np.uint32)
            piani = np.delete(semispazi, 3, axis = 1)
            for ss in segmenti_spaziati:
                visibile = False
                for s in ss[2:]:
                    spazio = piani[s]
                    if np.dot(lookvector, spazio) >= 0:
                        visibile = True
                if visibile:
                    segmenti = np.append(segmenti, [ss[:2]], axis=0)

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
                    semispazi = np.append(semispazi,[cut_vec],axis=0)
                elif event.key == pygame.K_q:
                    f = open("modello.json", "w")
                    json.dump(semispazi.tolist(), f)
                    f.close()
                    devochiudere = True
                elif event.key == pygame.K_l:
                    f = open("modello.json", "r")
                    semispazi = np.array(json.load(f))
                    f.close()

                    


        clock.tick(30)


    pygame.quit()

def preview():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((707, 1000))
    clock = pygame.time.Clock()

    with open(sys.argv[2], "r") as f:
        modello = json.load(f)

    punti = genera_punti(modello)
    segmenti = genera_segmenti(punti)

    primo_piano = int(punti[1][0][0])
    prima_faccia = [n for n,p in enumerate(punti[1]) if primo_piano in p]

    punto_zero = punti[0][prima_faccia[0]]
    vettore_uno = punti[0][prima_faccia[1]] - punto_zero
    lv = math.sqrt(sum(map(lambda x: x**2, vettore_uno)))
    vettore_uno = vettore_uno/lv
    vettore_due_pus = punti[0][prima_faccia[2]] - punto_zero
    vettore_due = vettore_due_pus - vettore_uno*np.dot(vettore_due_pus, vettore_uno)
    lv = math.sqrt(sum(map(lambda x: x**2, vettore_due)))
    vettore_due = vettore_due/lv
    verso = np.linalg.cross(vettore_uno, vettore_due)
    if np.dot(verso, punto_zero) < 0:
        vettore_due = -vettore_due

    primo_tassello = np.array([punti[0][n] - punto_zero for n in prima_faccia])
    matrice_appiattimento = np.append([vettore_uno], [vettore_due], axis=0)
    primo_tassello = np.dot(matrice_appiattimento, primo_tassello.transpose()).transpose()

    piani_occupati = {primo_piano}
    spigoli_da_ricercare = [s for s in segmenti if primo_piano in s[2:]]
    spigoli_di_riferimento = {s: (primo_tassello[prima_faccia.index(s[0])],primo_tassello[prima_faccia.index(s[1])]) for s in spigoli_da_ricercare}

    tasselli = [
            {
                'punti': primo_tassello,
                'faccia': primo_piano,
                'lati': []
            }
        ]

    rr = 0
    facce_prenotate = set()
    for s in spigoli_da_ricercare:
        d = [x for x in s[2:] if x != primo_piano][0]
        facce_prenotate.add(d)
    while len(spigoli_da_ricercare) > 0:
        rr += 1
        nuovi_spigoli = []
        for s in spigoli_da_ricercare:
            riferimento = spigoli_di_riferimento[s]
            piano = [p for p in s[2:] if p not in piani_occupati]
            piano = piano[0]
            faccia = [n for n,p in enumerate(punti[1]) if piano in p]
            s_conv = (faccia.index(s[0]),faccia.index(s[1]))
            punto_zero = punti[0][s[0]]
            vettore_uno = punti[0][s[1]] - punto_zero
            lv = math.sqrt(sum(map(lambda x: x**2, vettore_uno)))
            vettore_uno = vettore_uno/lv
            punto_due = [punti[0][p] for p in faccia if p not in s[:2]][0]
            vettore_due = punto_due - punto_zero
            vettore_due = vettore_due - vettore_uno*np.dot(vettore_due, vettore_uno)
            lv = math.sqrt(sum(map(lambda x: x**2, vettore_due)))
            vettore_due = vettore_due/lv
            verso = np.linalg.cross(vettore_uno, vettore_due)
            if np.dot(verso, punto_zero) < 0:
                vettore_due = -vettore_due
            tassello = np.array([punti[0][n] - punto_zero for n in faccia])
            matrice_appiattimento = np.append([vettore_uno], [vettore_due], axis=0)
            base_uno = riferimento[1]-riferimento[0]
            lv = math.sqrt(sum(map(lambda x: x**2, base_uno)))
            base_uno = base_uno/lv
            base_due = np.dot(np.array([[0,-1],[1,0]]), base_uno) # forse da cambiare
            base = np.append([base_uno], [base_due], axis = 0).transpose()
            
            tassello = np.dot(np.dot(base, matrice_appiattimento), tassello.transpose()).transpose() + riferimento[0]
            lati = []
            facce_prenotate.add(piano)
            for sn in segmenti:
                if piano in sn[2:]:
                    destinazione = [x for x in sn[2:] if x != piano][0]
                    if destinazione in piani_occupati.union(facce_prenotate):
                        lati.append((tassello[faccia.index(sn[0])],tassello[faccia.index(sn[1])]))
                    else:
                        nuovi_spigoli.append(sn)
                        spigoli_di_riferimento[sn] = (tassello[faccia.index(sn[0])],tassello[faccia.index(sn[1])])
                        facce_prenotate.add(destinazione)
            piani_occupati.add(piano)

            tasselli.append({
                'punti': tassello,
                'lati': lati,
                'faccia': piano
                })
        spigoli_da_ricercare = nuovi_spigoli


    rollio_deg = 0
    zoom = 1

    offset = np.array([354,500])
    tasselli.reverse()
    devochiudere = False
    while not devochiudere:
        screen.fill('black')
#        for i in range(4,707,50):
#            pygame.draw.line(screen, "yellow", (i, 0), (i, 1000))
#        for i in range(0,1000,50):
#            pygame.draw.line(screen, "yellow", (0, i), (707, i))
        rollio = rollio_deg*math.pi/180
        rotazione = np.array([[math.cos(rollio),-math.sin(rollio)],[math.sin(rollio),math.cos(rollio)]])
        for fec in tasselli:
            for s in fec['lati']:
                a = np.dot(rotazione,s[0]*100*zoom)+offset
                b = np.dot(rotazione,s[1]*100*zoom)+offset
                pygame.draw.line(screen, 'yellow', a, b, width=3)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                devochiudere = True
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    offset += np.array([10,0])
                elif event.key == pygame.K_LEFT:
                    offset += np.array([-10,0])
                elif event.key == pygame.K_UP:
                    offset += np.array([0,-10])
                elif event.key == pygame.K_DOWN:
                    offset += np.array([0,10])
                elif event.key == pygame.K_z:
                    rollio_deg -= 10
                elif event.key == pygame.K_c:
                    rollio_deg += 10
                elif event.key == pygame.K_s:
                    zoom += 1/16
                elif event.key == pygame.K_x:
                    zoom -= 1/16
                elif event.key == pygame.K_p:
                    stampa_tasselli(tasselli,rotazione,zoom,offset)

        clock.tick(30)

if __name__ == "__main__":
    if sys.argv[1] == "edit":
        sculpt()
    elif sys.argv[1] == "view":
        preview()
