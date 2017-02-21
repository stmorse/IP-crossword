from pulp import *
import random

class Grid:
    def __init__(self, N, blacksq=[]):
        self.N = N
        self.grid = [['-' for _ in range(N)] for _ in range(N)]
        for b in blacksq:
            if type(b) != tuple: 
                raise TypeError 
                break
            self.grid[b[0]][b[1]] = '#'
        
        # slot handling  *HACKY*
        self.positions = {'across': {}, 'down': {}}    # cell->position w/in word
        self.slots     = {'across': {}, 'down': {}}    # cell->slot e.g. (2, across)  
        self.sizes     = {'across': {}, 'down': {}}    # cell->slot size
        self.allslots  = []     # list of all slots
        cgrid = [[c for c in self.grid[i]] for i in range(len(self.grid))]
        for d in ['across','down']:
            sx = 0
            for i, row in enumerate(cgrid):
                line = ''.join(row)
                blocks = line.split('#')
                jcounter = 0
                for b in blocks:
                    if len(b) == 0:
                        jcounter += 1
                        continue
                    elif len(b) == 1:
                        jcounter += 2
                        continue
                    for bcounter in range(len(b)):
                        cell = (i,jcounter) if d=='across' else (jcounter,i)
                        self.positions[d][cell] = bcounter
                        self.slots[d][cell] = (sx,d)
                        self.sizes[d][cell] = len(b)
                        jcounter += 1
                    self.allslots.append((sx,d))
                    sx += 1
                    jcounter += 1
            cgrid = map(list, zip(*cgrid))   # transpose grid
        self.sizebyslot = {d: {self.slots[d][cell][0]: self.sizes[d][cell] for cell in self.slots[d]} \
                           for d in self.slots}
            
    def getPositionAt(self, cell, d):
        return self.positions[d][cell] if cell in self.positions[d] else None
    
    def getSlotAt(self, cell, d):
        return self.slots[d][cell] if cell in self.slots[d] else None
    
    def getSizeAt(self, cell, d):
        return self.sizes[d][cell] if cell in self.sizes[d] else None
    
    def getAllSlots(self):
        return self.allslots
    
    def getSlotSize(self, slot):
        return self.sizebyslot[slot[1]][slot[0]]
    
    def iterCells(self):
        for i in range(N):
            for j in range(N):
                if self.grid[i][j] != '#':
                    yield (i,j)
    
    def __repr__(self):
        str = ''
        for r in self.grid:
            for c in r:
                str += c + ' '
            str += '\n'
        return str


class IPXWordGenerator:
	def __init__(self, G, numk=-1):
		self.G = G
		self.slots = self.G.getAllSlots()
		self.N = self.G.N    # dimension of puzzle
		self.numk = numk     # number of words to sample

		print('GRID:')
		print(self.G)

		print('Number slots: %d' % len(self.slots))

		# load dictionary of words as set
		allwords0 = []
		with open('ospd.txt', 'r') as f:
		    allwords0 = [w.strip() for w in f.readlines()]
		psz = set([G.getSlotSize(s) for s in G.getAllSlots()])
		print('Different word lengths possible:', psz)
		allwords = []
		for size in psz:
		    allwords.extend([w for w in allwords0 if len(w)==size])

		self.allwords = allwords
		if numk > 0:
			self.allwords = random.sample(allwords, numk)
		print('Dictionary size after sampling: %d' % len(self.allwords))

		print('(Using random word values.)')
		self.allcosts = [random.randint(0,100) for w in self.allwords]
		self.allposs = self._preprocess()


	def _preprocess(self):
		# preprocessing step: 
		# build dict of all possible words for each cell/direction
		allposs = {}
		for i in range(self.N):   # row
		    for j in range(self.N):   # col
		        c = (i,j)
		        allposs[c] = {}
		        pos = {d: self.G.getPositionAt(c,d) for d in ['across', 'down']}
		        for let in 'abcdefghijklmnopqrstuvwxyz':
		            allposs[c][let] = {}
		            for d in ['across', 'down']:
		                allposs[c][let][d] = \
		                    set([(k,w) for k,w in enumerate(self.allwords) \
		                         if  len(w) == self.G.getSizeAt(c, d) \
		                         and w[pos[d]] == let])
		return allposs


	def set_words(self, include=[], assign={}):
		# this method will set mandatory included words in the puzzle:
		# `include` : list of words that should be included somewhere
		# `assign` : dict of cell-to-word assignments
		print('TODO: add this functionality.  :(')


	def build(self):
		print('\nBuilding...')

		prob = LpProblem("puzzle", LpMaximize)

		poss_combos = [(w, s) for w in range(len(self.allwords)) for s in self.slots]
		self.zvars = LpVariable.dicts('zvars', poss_combos, 0, 1, LpBinary) 

		# Constr (1) : every word appears once or not at all (numk constraints)
		for k in range(self.numk):
		    prob += lpSum(self.zvars[(k,s)] for s in self.slots) <= 1
		    
		# Constr (2) : all slots assigned to exactly one word (len(slots) constraints)
		for s in self.slots:
		    prob += lpSum(self.zvars[(k,s)] for k in range(self.numk)) == 1
		    
		# Constr (2a) : slots must contain a feasible word
		for s in self.slots:
		    ssize = self.G.getSlotSize(s)
		    for k in range(self.numk):
		        if len(self.allwords[k]) != ssize:
		            prob += self.zvars[(k,s)] == 0
		    
		# Constr (3) : in every cell, zvars must match
		for i in range(self.N):
		    for j in range(self.N):
		        c = (i,j)
		        slota = self.G.getSlotAt(c, 'across')
		        slotd = self.G.getSlotAt(c, 'down')
		        for let in 'abcdefghijklmnopqrstuvwxyz':
		            rowx = [rt[0] for rt in self.allposs[c][let]['across']]
		            colx = [ct[0] for ct in self.allposs[c][let]['down']]
		            
		            if len(rowx)==0 or len(colx)==0:
		                for k in rowx:
		                    prob += self.zvars[(k,slota)] == 0
		                for k in colx:
		                    prob += self.zvars[(k,slotd)] == 0
		                continue
		                
		            prob += lpSum(self.zvars[(k1,slota)] for k1 in rowx) == \
		                    lpSum(self.zvars[(k2,slotd)] for k2 in colx)
	                
		# Objective : random costs for now
		prob += lpSum(self.allcosts[k] * self.zvars[(k,s)] \
					  for k in range(self.numk) for s in self.slots)

		status = prob.solve()

		print('Puzzle status:', LpStatus[status])


	def get_puzzle(self):
		count = 0
		self.finalw = []
		for k in range(self.numk):
		    for s in self.slots:
		        if value(self.zvars[(k,s)]) > 0:
		            count += 1
		            self.finalw.append((k, s, self.allwords[k]))
		print('\nTotal words:', count)
		print('Assignments: (index, (slot), word)')
		for l in self.finalw:
		    print(l)


if __name__ == '__main__':
	G = Grid(3, blacksq=[(0,0)])
	ipx = IPXWordGenerator(G, numk=500)
	ipx.build()
	ipx.get_puzzle()
	

