import argparse
import sys
import random
import string
import math

LOWER_CASE = "abcdefghijklmnopqrstuvwxyz"
UPPER_CASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
SYMBOLS = "!@#$%^&*()_+=-[]{}|;’:/,.<>?\\\""
SPACE = " "
VAL_CHARS = (LOWER_CASE + UPPER_CASE + DIGITS \
			+ SYMBOLS + SPACE)

"""
Genetic Algorithm Class that matches the target string :
"I think this is a reasonable medium sized string!!"

Takes command like arguments:
	individuals
	selectionType
	crossoverProbability
	mutationProbability
	generations
	displayInterval
"""
class GeneticAlgorithm(object):

	def __init__(self, args):

		self.numIndividuals = int(args.individuals)
		self.selectionType = args.selectionType
		self.crossProb = float(args.crossoverProbability)
		self.mutationProb = float(args.mutationProbability)
		self.numGens = int(args.generations)
		self.disInt = int(args.displayInterval)
		self.target = "I think this is a reasonable medium sized string!!"
		self.population = [] #array to hold population
		#individuals are stored as tuples, the first item being the sequence and the sencond being fitness
		self.populate() #populates array
		#self.data = []

	#Helper funciton to generate random strings
	#Takes length of target string as an argument for better adaptability
	def randomString(self, strLen):
   		return ''.join(random.choice(VAL_CHARS) for x in range(strLen))

   	#Returns a populated population array  
	def populate(self):

   		population = []

   		for indv in range(self.numIndividuals):
   			start = self.randomString(len(self.target))
   			self.population.append((start, self.calcFitness(start)))

   		return population

   	#Mutation function
   	#Takes a parent string and returns a (possibly) mutated child
   	#Note that randomness is built-in to mutate function
	def mutate(self, parentString):

		charList = list(parentString) #turn string into list of characters
		index = 0 #used to index characters

		for letter in charList:
			#random flaot value between 0 and 1
			chance = round(random.uniform(0, 1), 2)

			if self.mutationProb >= chance:
				#replace letter with random one from valid characters
				charList[index] = random.choice(VAL_CHARS)

			index += 1

		return "".join(charList) #join character list into a string

	#Cross-over function
	#takes two parent strings and returns array of two child strings
	def crossOver(self, parent1, parent2):

		#set kids equal to parents
		child1 = parent1
		child2 = parent2
		chance = round(random.uniform(0, 1), 2)

		if self.crossProb >= chance:

			#chooses random index within length of parent strings
			crossIndex = random.randint(0, len(parent1) - 1)

			#preform swap
			child1 = parent1[:crossIndex] + parent2[crossIndex:]
			child2 = parent2[:crossIndex] + parent1[crossIndex:]

		children = [child1, child2]
		return children


	#Funciton to display current best individual
	#Takes generation number, best sequence, and number of correct characters
	def display(self, genNum, bestSeq, bestFitness):

		print(str(genNum) + "( " + str(bestFitness) + "/50 = " \
			+ str(bestFitness/len(bestSeq)) + "):  " + bestSeq)
	
	#Helper function to calculate fitness
	#Takes a string and returns the number of correct characters
	def calcFitness(self, sequence):

		charsCorrect = 0

		#iterate through passed-in string and target string in parallel
		for test, target in zip(sequence, self.target):

			if test == target:
				charsCorrect += 1

		return charsCorrect

	#Main evolution wrapper function
	def evolve(self):

		for gen in range(self.numGens + 1):

			bPool = [] #array to hold breeding pool
			offspring = [] #array to hold new generation

			if (gen % self.disInt == 0 or gen == self.numGens): #checks if best candidate should be displayed

				best = ["", 0] #array to hold best candidate
				for indv in self.population:

					if (indv[1] >= best[1]): #checks fitness against best for each indv
						best[1] = indv[1] #updates best if better than previously found
						best[0] = indv[0] #updates coresponding string

				#make call to display
				self.display(gen, best[0], best[1])
				#Check to see if target string has been reached or max generations has been reached
				if (best[1] == 50):
					print("Target string reached: " + best[0])
					self.calcAverageFitness()
					break
				#If last generation
				elif (gen == self.numGens):
					print("Target not matched. Best canidate: " + best[0])
					#Calculate average fitness
					self.calcAverageFitness()
					break

			#If rank selection
			if self.selectionType == "rs":

				probabilities = [] #will hold breeding pool probabilities
				rankSum = sum(range(self.numIndividuals)) #sum of ranks
				
				#sorts population by fitness
				self.population.sort(key=lambda tup: tup[1])  
				#calculate probability for each individual
				rank = 0
				while rank < len(self.population):
					probabilities.append(rank / rankSum)
					rank += 1

				#select individuls for the breeding pool
				cumulativeProbs = [] #holds cumulative probabilities
				counter = 0
				for prob in probabilities:
					counter += prob
					cumulativeProbs.append(counter)

				#Choose individuals for the breeding pool
				for i in range(len(self.population)):
					chance = random.uniform(0, 1)
					for j in range(len(cumulativeProbs)):
						#append first individual that meets the chance threshhold
						if (cumulativeProbs[j] >= chance):
							bPool.append(self.population[j])
							#then break
							break

				#now do recombination and mutation
				#itterate by 2s
				parent = 0
				while parent < len(bPool):

					parent1 = bPool[parent]
					parent2 = bPool[parent + 1]
					children = self.crossOver(parent1[0], parent2[0])
					child1 = self.mutate(children[0])
					child2 = self.mutate(children[1])
					offspring.append((child1, self.calcFitness(child1)))
					offspring.append((child2, self.calcFitness(child2)))

					parent += 2

				#Set population to new generation
				self.population = offspring

			#Bozeman
			if self.selectionType == "bs":

				probabilities = []
				fitnesses = []
				fitnessSum = 0 

				#calculate fitness sum
				for indv in self.population:
					#Tried to use 'math.e ** (indv[1] / len(indv[0]))' but it didn't work
					fitness = math.e ** (indv[1])
					fitnesses.append(fitness)
					fitnessSum += fitness

				#calculate probability for each individual
				indv = 0
				while indv < len(self.population):
					probabilities.append(fitnesses[indv] / fitnessSum)
					indv += 1
					
				#select individuls for the breeding pool
				cumulativeProbs = []
				counter = 0
				for prob in probabilities:
					counter += prob
					cumulativeProbs.append(counter)

				#print(cumulativeProbs)

				for i in range(len(self.population)):
					chance = random.uniform(0, 1)
					for j in range(len(cumulativeProbs)):
						if (cumulativeProbs[j] >= chance):
							bPool.append(self.population[j])
							break

				#now do recombination and mutation
				#itterate by 2s
				parent = 0
				while parent < len(bPool):

					parent1 = bPool[parent]
					parent2 = bPool[parent + 1]
					children = self.crossOver(parent1[0], parent2[0])
					child1 = self.mutate(children[0])
					child2 = self.mutate(children[1])
					offspring.append((child1, self.calcFitness(child1)))
					offspring.append((child2, self.calcFitness(child2)))
					parent += 2

				self.population = offspring
			
			#Tournament
			if self.selectionType == "ts":

				parentSel = 0 #counter for adding individuals to breeding pool
				while parentSel < len(self.population):

					#Choose two random individuals
					indv1 = random.choice(self.population)
					indv2 = random.choice(self.population)

					#Check which is more fit and add to breeding pool
					if indv1[1] >= indv2[1]:
						bPool.append(indv1)
					else:
						bPool.append(indv2)

					parentSel += 1
				
				#now do recombination and mutation
				#itterate by 2s
				parent = 0
				while parent < len(bPool):

					parent1 = bPool[parent]
					parent2 = bPool[parent + 1]
					children = self.crossOver(parent1[0], parent2[0])
					child1 = self.mutate(children[0])
					child2 = self.mutate(children[1])
					offspring.append((child1, self.calcFitness(child1)))
					offspring.append((child2, self.calcFitness(child2)))
					parent += 2
					
				self.population = offspring

	def calcAverageFitness(self):
		fitnesses = []
		average = 0

		for indv in self.population:
			fitnesses.append(indv[1] / len(indv[0]))

		for fitness in fitnesses:
			average += fitness

		print("Average fitness: " + str(average / len(fitnesses)))

#Function to read in and parse command line args
def getArgs():

	# create parser
	parser = argparse.ArgumentParser()
	 
	# add arguments to the parser
	parser.add_argument("individuals")
	parser.add_argument("selectionType")
	parser.add_argument("crossoverProbability")
	parser.add_argument("mutationProbability")
	parser.add_argument("generations")
	parser.add_argument("displayInterval")
	 
	# parse the arguments
	return parser.parse_args()


def main(args):

	#create genetic algorithm
	GA = GeneticAlgorithm(args);
	#Start evolution
	GA.evolve()


if __name__ == '__main__':

	#parse args
	args = getArgs()
	#call main funciton
	main(args)


