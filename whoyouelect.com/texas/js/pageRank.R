# EXACT SMALL-SCALE COMPUTATION OF PAGERANK
# H = adjacency matrix
# b = bookmark vector
# alpha = balancing parameter

exact.pr = function (H, b, alpha = 0.85) {
  
  n = dim(H)[1]
  # normalize adjacency matrix by row sum and 
  # replace dangling rows with bookmark vector (S matrix)
  S = H
  # compute row sums
  rs = H %*% rep(1,n)
  for (i in 1:n) {
    if (rs[i] == 0) {
      S[i,] = b
    } else {
      S[i,] = S[i,] / rs[i]   
    }  
  }
  
  # build teleportation matrix 
  T = rep(1, n) %*% t(b)
  
  # build Google matrix 
  G = alpha * S + (1-alpha) * T
  
  # compute eigenpairs and retrieve the leading eigenvector
  eig = eigen(t(G))
  #pi = as.real(eig$vectors[,1])
  pi = as.numeric(eig$vectors[,1])
  pi = pi / sum(pi)
  return(pi)
}





# APPROXIMATED SMALL-SCALE COMPUTATION OF PAGERANK (uses dense matrix G)
# H = adjacency matrix
# b = bookmark vector
# alpha = balancing parameter
# t = number of digits of precision
# S = Google Matrix

approx.pr = function (H, b, alpha = 0.85, t = 3) {
  
  n = dim(H)[1]
  # normalize adjacency matrix by row sum and 
  # replace dangling rows with bookmark vector (S matrix)
  S = H
  # compute row sums
  rs = H %*% rep(1,n)
  
  for (i in 1:n) {
    if (rs[i] == 0) {
      S[i,] = b
    } else {
      S[i,] = S[i,] / rs[i]   
    }  
  }
  
  
  # build teleportation matrix 
  T = rep(1, n) %*% t(b)
  
  # build Google matrix 
  G = alpha * S + (1-alpha) * T
  
  pi0 = rep(0, n)
  pi1 = rep(1/n, n)
  eps = 1/10^t
  iter = 0
  while (sum(abs(pi0 - pi1)) > eps) {
    pi0 = pi1
    pi1 = pi1 %*% G
    iter = iter + 1
  } 
  pi1 = pi1 / sum(pi1)
  return(list(pi = pi1, iter = iter))
}



randG = function(n, p) {
  adj =  matrix(nrow=n, ncol=n)
  for (i in 1:n) {
    adj[i,] = sample(c(0,1), n, replace=TRUE, prob=c(1-p, p))
  }
  return(adj)
}


#from https://users.dimi.uniud.it/~massimo.franceschet/R/pagerank.html

n = 1000;
p = 0.1;
H = randG(n, p)     #1000 x 1000 adjacency matrix  
b = rep(1/n, n)     #array of size 1000 
alpha = 0.85
t = 10

system.time(exact.pr(H, b, alpha))
#user  system elapsed 
#6.424   0.932 101.097 

system.time(approx.pr(H, b, alpha, t))  
#user  system elapsed 
#.077   0.036   1.408 




