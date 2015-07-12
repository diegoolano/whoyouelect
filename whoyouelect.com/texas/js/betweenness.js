//adapted from https://gist.github.com/mhawksey/1683530
//this still takes too long since its of the order of V * V *E 

function compute_betweenness(matrix,ncols){
  var betweenness = [];
  var bMax = 0;
  for(var i=0; i<ncols; i++){ betweenness[i]=0; }
  for(var s=0; s<ncols; s++){
    var stack=[],
            P=[],
            sigma=[],
            dist=[];
    for(i=0;i<ncols;i++){
        P[i]=[];
        if(i==s){
            sigma[i]=1;
            dist[i]=0;
        }else{
            sigma[i]=0;
            dist[i]=-1;
        }
    }
    var queue=[];
    queue.push(s);
    
    while(queue.length > 0){
      var v=queue.shift();
      stack.push(v);
      for(var w=0; w<ncols; w++){
        //if(matrix[v][w]==1){
        if(matrix[v][w] > 0){
            if(dist[w] < 0){
                queue.push(w);
                dist[w]=dist[v] + 1;
            }
            if(dist[w]==dist[v] + 1){
                sigma[w]=sigma[w] +sigma[v];
                P[w][P[w].length] = v;
            }
        }
      }
    }
    var delta=[];
    for(var i=0; i<ncols; i++){
      delta[i]=0;
    }
    while(stack.length>0){
      w=stack.pop();
      for(var i=0; i<P[w].length; i++){
              v=P[w][i]; 
              delta[v] +=(sigma[v] /sigma[w]) * (1 +delta[w]);
      }
      if(w != s){			
              betweenness[w] +=delta[w];
      }
    }
  }
  for (var i=0; i<ncols; i++){
    betweenness[i]=[(betweenness[i]/(2))];
    if (betweenness[i] > bMax) bMax = betweenness[i][0];
  }
  return betweenness;
}
function calcBetweenness(edge_data,og_vals_to_id,userlength){
   //initialize matrix
   var matrix = [];
   for (i=0; i < userlength; i++){ 
	   matrix[i]=[];    
	   for (j=0; j < userlength; j++){ 
		matrix[i][j]=0;
	   }
   }    

   //construct adjacency matrix
   for (e=0; i <edge_data.length; e++){
	ed = edge_data[e];
	if( String(ed) != "undefined"){ 
		sr = og_vals_to_id[ed.source];
		tr = og_vals_to_id[ed.target];
		matrix[sr][tr] = 1;
		matrix[tr][sr] = 1;
	}
   } 

  return compute_betweenness(matrix,userlength);
}
