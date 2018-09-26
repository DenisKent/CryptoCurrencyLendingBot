from loanTrackerTools import cliffFinder

curve1 = [{'rate':0.07,'amount':0.1},{'rate':0.16,'amount':0.6},{'rate':0.19,'amount':0.3},{'rate':0.20,'amount':1.0}]
curve2 = [{'rate':0.07,'amount':1.4},{'rate':0.08,'amount':1.1}]
curve3 = [{'rate':0.07,'amount':1.5}]
curve4 = []


print cliffFinder(curve1,1.0)
print cliffFinder(curve2,1.0)
print cliffFinder(curve3,1.0)
print cliffFinder(curve4,1.0)