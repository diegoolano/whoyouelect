self.addEventListener('message', function(e) {
  //here you are getting passed centernode and other variables/function as message to populate stats panel
  populate_stats_page_async(e.data, function(xhr){
		var result = xhr;
		setTimeout(function() { sendback(); }, 200);
		function sendback(){ self.postMessage(result); }
  });

}, false);


//var highlightlock; // can i set this from other file?
function populate_stats_page_async(centernode,callback){


	//sworker.postMessage([center_node,distmetric,graph2,name_to_index,near_co,same_art_co]);	

	//still need samesentop, samesentandnearop, samesentneararticleop, samearticleop
	distmetric = centernode[1];
	graph2 = centernode[2];
	name_to_index = centernode[3];
	near_co = centernode[4];
	same_art_co = centernode[5];
	samesentop = centernode[6];
	samesentandnearop = centernode[7];
	samesentneararticleop = centernode[8];
        samearticleop = centernode[9];
	centernode = centernode[0];

	//see if it just works
	//need distmetric, 
	//need graph2, name_to_index, 

	//CHANGED ALL j references to graph2

	if(centernode == "J.D. Sheffield"){centernode = "Sheffield"; }
	highlightlock = 0;	

	//returns [output,polobj,orgobj,perobj,locobj,billobj,miscobj];
	if( distmetric == "comb" || distmetric == "ss"){ op = samesentop; }
	else{ op = get_most_sentences_async(centernode,"same sentence");}
	top_objs = "<table class='restable' style='border-bottom:3px dashed; width:950px'><tr style='vertical-align:top'><td width='17%'><h1><a href='javascript: showstat(0);'>Top Associated</a><br/><span class='small'>same sentence</span></h1></td><td width='17%'><h1><a href='javascript: showstat(1);'>Top Associated</a><br/><span class='small'>same sentence/near</span></h1></td><td width='17%'><h1><a href='javascript: showstat(2);'>Top Associated</a><br/><span class='small'>same sentence/near/article</span></h1></td><td width='17%'><h1><a href='javascript: showstat(3);'>Top Associated</a><br/><span class='small'>same article only (not near)</span></h1></td><td width='17%'><h1><a href='javascript: showstat(4);'>Top Associated</a><br/><span class='small'>combined  metric</span></h1></td><td width='17%'><h1><a href='javascript: showstat(5);'>Summary</a><br/><span class='small'>comparison</span></h1></td></tr></table>"+op[0];
	pol = []; for(p in op[1]){ pol.push([p,op[1][p]]);} pol.sort(function(a, b) {return a[1] - b[1]}).reverse(); 
	org = []; for(p in op[2]){ org.push([p,op[2][p]]);} org.sort(function(a, b) {return a[1] - b[1]}).reverse();
	per = []; for(p in op[3]){ per.push([p,op[3][p]]);} per.sort(function(a, b) {return a[1] - b[1]}).reverse();
	loc = []; for(p in op[4]){ loc.push([p,op[4][p]]);} loc.sort(function(a, b) {return a[1] - b[1]}).reverse();
	bill = []; for(p in op[5]){ bill.push([p,op[5][p]]);} bill.sort(function(a, b) {return a[1] - b[1]}).reverse();
	misc = []; for(p in op[6]){ misc.push([p,op[6][p]]);} misc.sort(function(a, b) {return a[1] - b[1]}).reverse();

	billout = ""; miscout = "";
	polout = "Politicians: <ul>"; pol.forEach(function(d){ polout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	orgout = "Organizations: <ul>"; org.forEach(function(d){ orgout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	perout = "Persons: <ul>"; per.forEach(function(d){ perout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	locout = "Locations: <ul>"; loc.forEach(function(d){ locout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	if(Object.keys(op[5]).length > 0){ billout = "Bills: <ul>"; bill.forEach(function(d){ billout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }
	if(Object.keys(op[6]).length > 0){ miscout = "Misc: <ul>"; misc.forEach(function(d){ miscout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }

	colout = "<tr><td colspan=2><table class='innerres'><tr style='vertical-align:top'><td>"+polout+"</td><td>"+orgout+"</td><td>"+perout+"</td><td>"+locout+"</td><td>"+billout+"</td><td>"+miscout+"</td></tr></table></td></tr></table>";

	out = {}
	out['same sentence'] = [ polout, orgout, perout,locout,billout,miscout];

	newmetric_list = {'pol':{}, 'org':{}, 'per':{}, 'loc':{}, 'bill':{}, 'misc':{}};
	pol.forEach(function(d){ newmetric_list['pol'][d[0]] = {'same sentence':d[1]};});
	org.forEach(function(d){ newmetric_list['org'][d[0]] = {'same sentence':d[1]};});
	per.forEach(function(d){ newmetric_list['per'][d[0]] = {'same sentence':d[1]};});
	loc.forEach(function(d){ newmetric_list['loc'][d[0]] = {'same sentence':d[1]};});
	bill.forEach(function(d){ newmetric_list['bill'][d[0]] = {'same sentence':d[1]};});
	misc.forEach(function(d){ newmetric_list['misc'][d[0]] = {'same sentence':d[1]};});


	//same and near
	if( distmetric == "comb" || distmetric == "sn"){ op = samesentandnearop; }
	else{ op = get_most_sentences_async(centernode,"same and near sentence"); }	

	top_objs2 = op[0]
	pol = []; for(p in op[1]){ pol.push([p,op[1][p]]);} pol.sort(function(a, b) {return a[1] - b[1]}).reverse(); 
	org = []; for(p in op[2]){ org.push([p,op[2][p]]);} org.sort(function(a, b) {return a[1] - b[1]}).reverse();
	per = []; for(p in op[3]){ per.push([p,op[3][p]]);} per.sort(function(a, b) {return a[1] - b[1]}).reverse();
	loc = []; for(p in op[4]){ loc.push([p,op[4][p]]);} loc.sort(function(a, b) {return a[1] - b[1]}).reverse();
	bill = []; for(p in op[5]){ bill.push([p,op[5][p]]);} bill.sort(function(a, b) {return a[1] - b[1]}).reverse();
	misc = []; for(p in op[6]){ misc.push([p,op[6][p]]);} misc.sort(function(a, b) {return a[1] - b[1]}).reverse();

	billout = ""; miscout = "";
	polout = "Politicians: <ul>"; pol.forEach(function(d){ polout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	orgout = "Organizations: <ul>"; org.forEach(function(d){ orgout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	perout = "Persons: <ul>"; per.forEach(function(d){ perout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	locout = "Locations: <ul>"; loc.forEach(function(d){ locout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	if(Object.keys(op[5]).length > 0){ billout = "Bills: <ul>"; bill.forEach(function(d){ billout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }
	if(Object.keys(op[6]).length > 0){ miscout = "Misc: <ul>"; misc.forEach(function(d){ miscout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }

	colout2 = "<tr><td colspan=2><table class='innerres'><tr style='vertical-align:top'><td>"+polout+"</td><td>"+orgout+"</td><td>"+perout+"</td><td>"+locout+"</td><td>"+billout+"</td><td>"+miscout+"</td></tr></table></td></tr></table>";

	out['same and near sentence'] = [ polout, orgout, perout,locout,billout,miscout];
	pol.forEach(function(d){ if(d[0] in newmetric_list['pol']){newmetric_list['pol'][d[0]]['same and near sentence']=d[1];}else{newmetric_list['pol'][d[0]] = {'same and near sentence':d[1]};}});
	org.forEach(function(d){ if(d[0] in newmetric_list['org']){newmetric_list['org'][d[0]]['same and near sentence']=d[1];}else{newmetric_list['org'][d[0]] = {'same and near sentence':d[1]};}});
	per.forEach(function(d){ if(d[0] in newmetric_list['per']){newmetric_list['per'][d[0]]['same and near sentence']=d[1];}else{newmetric_list['per'][d[0]] = {'same and near sentence':d[1]};}});
	loc.forEach(function(d){ if(d[0] in newmetric_list['loc']){newmetric_list['loc'][d[0]]['same and near sentence']=d[1];}else{newmetric_list['loc'][d[0]] = {'same and near sentence':d[1]};}});
	bill.forEach(function(d){ if(d[0] in newmetric_list['bill']){newmetric_list['bill'][d[0]]['same and near sentence']=d[1];}else{newmetric_list['bill'][d[0]] = {'same and near sentence':d[1]};}});
	misc.forEach(function(d){ if(d[0] in newmetric_list['misc']){newmetric_list['misc'][d[0]]['same and near sentence']=d[1];}else{newmetric_list['misc'][d[0]] = {'same and near sentence':d[1]};}});

	//same and near sentences and same article
	if( distmetric == "comb"){ op = samesentneararticleop; }
	else{ op = get_most_sentences_async(centernode,"combined same, near, article"); }
	top_objs3 = op[0]
	pol = []; for(p in op[1]){ pol.push([p,op[1][p]]);} pol.sort(function(a, b) {return a[1] - b[1]}).reverse(); 
	org = []; for(p in op[2]){ org.push([p,op[2][p]]);} org.sort(function(a, b) {return a[1] - b[1]}).reverse();
	per = []; for(p in op[3]){ per.push([p,op[3][p]]);} per.sort(function(a, b) {return a[1] - b[1]}).reverse();
	loc = []; for(p in op[4]){ loc.push([p,op[4][p]]);} loc.sort(function(a, b) {return a[1] - b[1]}).reverse();
	bill = []; for(p in op[5]){ bill.push([p,op[5][p]]);} bill.sort(function(a, b) {return a[1] - b[1]}).reverse();
	misc = []; for(p in op[6]){ misc.push([p,op[6][p]]);} misc.sort(function(a, b) {return a[1] - b[1]}).reverse();

	billout = ""; miscout = "";
	polout = "Politicians: <ul>"; pol.forEach(function(d){ polout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	orgout = "Organizations: <ul>"; org.forEach(function(d){ orgout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	perout = "Persons: <ul>"; per.forEach(function(d){ perout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	locout = "Locations: <ul>"; loc.forEach(function(d){ locout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	if(Object.keys(op[5]).length > 0){ billout = "Bills: <ul>"; bill.forEach(function(d){ billout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }
	if(Object.keys(op[6]).length > 0){ miscout = "Misc: <ul>"; misc.forEach(function(d){ miscout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }


	colout3 = "<tr><td colspan=2><table class='innerres'><tr style='vertical-align:top'><td>"+polout+"</td><td>"+orgout+"</td><td>"+perout+"</td><td>"+locout+"</td><td>"+billout+"</td><td>"+miscout+"</td></tr></table></td></tr></table>";
	out['combined same, near, article'] = [ polout, orgout, perout,locout,billout,miscout];

	pol.forEach(function(d){ if(d[0] in newmetric_list['pol']){newmetric_list['pol'][d[0]]['combined same, near, article']=d[1];}else{newmetric_list['pol'][d[0]] = {'combined same, near, article':d[1]};}});
	org.forEach(function(d){ if(d[0] in newmetric_list['org']){newmetric_list['org'][d[0]]['combined same, near, article']=d[1];}else{newmetric_list['org'][d[0]] = {'combined same, near, article':d[1]};}});
	per.forEach(function(d){ if(d[0] in newmetric_list['per']){newmetric_list['per'][d[0]]['combined same, near, article']=d[1];}else{newmetric_list['per'][d[0]] = {'combined same, near, article':d[1]};}});
	loc.forEach(function(d){ if(d[0] in newmetric_list['loc']){newmetric_list['loc'][d[0]]['combined same, near, article']=d[1];}else{newmetric_list['loc'][d[0]] = {'combined same, near, article':d[1]};}});
	bill.forEach(function(d){ if(d[0] in newmetric_list['bill']){newmetric_list['bill'][d[0]]['combined same, near, article']=d[1];}else{newmetric_list['bill'][d[0]] = {'combined same, near, article':d[1]};}});
	misc.forEach(function(d){ if(d[0] in newmetric_list['misc']){newmetric_list['misc'][d[0]]['combined same, near, article']=d[1];}else{newmetric_list['misc'][d[0]] = {'combined same, near, article':d[1]};}});

	//same article only  TODO for efficiency sake possibly redo this as its just:  article_only =    ['combined same, near, article'] - ( ['same and near sentence']) ;
	if( distmetric == "comb"){ op = samearticleop; }
	else{ op = get_most_sentences_async(centernode,"same article"); }	

	top_objs4 = op[0]
	pol = []; for(p in op[1]){ pol.push([p,op[1][p]]);} pol.sort(function(a, b) {return a[1] - b[1]}).reverse(); 
	org = []; for(p in op[2]){ org.push([p,op[2][p]]);} org.sort(function(a, b) {return a[1] - b[1]}).reverse();
	per = []; for(p in op[3]){ per.push([p,op[3][p]]);} per.sort(function(a, b) {return a[1] - b[1]}).reverse();
	loc = []; for(p in op[4]){ loc.push([p,op[4][p]]);} loc.sort(function(a, b) {return a[1] - b[1]}).reverse();
	bill = []; for(p in op[5]){ bill.push([p,op[5][p]]);} bill.sort(function(a, b) {return a[1] - b[1]}).reverse();
	misc = []; for(p in op[6]){ misc.push([p,op[6][p]]);} misc.sort(function(a, b) {return a[1] - b[1]}).reverse();

	billout = ""; miscout = "";
	polout = "Politicians: <ul>"; pol.forEach(function(d){ polout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	orgout = "Organizations: <ul>"; org.forEach(function(d){ orgout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	perout = "Persons: <ul>"; per.forEach(function(d){ perout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	locout = "Locations: <ul>"; loc.forEach(function(d){ locout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	if(Object.keys(op[5]).length > 0){ billout = "Bills: <ul>"; bill.forEach(function(d){ billout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }
	if(Object.keys(op[6]).length > 0){ miscout = "Misc: <ul>"; misc.forEach(function(d){ miscout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }

	colout4 = "<tr><td colspan=2><table class='innerres'><tr style='vertical-align:top'><td>"+polout+"</td><td>"+orgout+"</td><td>"+perout+"</td><td>"+locout+"</td><td>"+billout+"</td><td>"+miscout+"</td></tr></table></td></tr></table>";
	out['same article'] = [ polout, orgout, perout,locout,billout,miscout];

	pol.forEach(function(d){ if(d[0] in newmetric_list['pol']){newmetric_list['pol'][d[0]]['same article']=d[1];}else{newmetric_list['pol'][d[0]] = {'same article':d[1]};}});
	org.forEach(function(d){ if(d[0] in newmetric_list['org']){newmetric_list['org'][d[0]]['same article']=d[1];}else{newmetric_list['org'][d[0]] = {'same article':d[1]};}});
	per.forEach(function(d){ if(d[0] in newmetric_list['per']){newmetric_list['per'][d[0]]['same article']=d[1];}else{newmetric_list['per'][d[0]] = {'same article':d[1]};}});
	loc.forEach(function(d){ if(d[0] in newmetric_list['loc']){newmetric_list['loc'][d[0]]['same article']=d[1];}else{newmetric_list['loc'][d[0]] = {'same article':d[1]};}});
	bill.forEach(function(d){ if(d[0] in newmetric_list['bill']){newmetric_list['bill'][d[0]]['same article']=d[1];}else{newmetric_list['bill'][d[0]] = {'same article':d[1]};}});
	misc.forEach(function(d){ if(d[0] in newmetric_list['misc']){newmetric_list['misc'][d[0]]['same article']=d[1];}else{newmetric_list['misc'][d[0]] = {'same article':d[1]};}});

	//New Metric is basically (1*samesent + 8/10*near + 1/10same article) * something to penalize based on how many times you are just "same article" as a proportion of your total!
	//for now, try      (samesent+near+samearticle)/ ( samearticle+samesent+near - samearticle )   <--- this way people who are mostly just same articles will be punished for it 
	//?? do i need to account for difference between two people who are both largely just samearticle references if one has a whole bunch of mentiones and the other one few?
	//----- for this last one, i think i'd need to know how much they touch other people..

	nodeweights = {'pol':[], 'org':[], 'per':[], 'loc':[], 'bill':[], 'misc':[]};
	for( pk in nodeweights ){
		Object.keys(newmetric_list[pk]).forEach(function(k){ 
			nk = newmetric_list[pk][k]; 
			if( typeof(nk['same sentence']) == "undefined"){ newmetric_list[pk][k]['same sentence'] = 0; }
			if( typeof(nk['same and near sentence']) == "undefined"){ newmetric_list[pk][k]['same and near sentence'] = 0; }
			if( typeof(nk['combined same, near, article']) == "undefined"){ newmetric_list[pk][k]['combined same, near, article'] = 0; }
			if( typeof(nk['same article']) == "undefined"){ newmetric_list[pk][k]['same article'] = 0; }
			nk = newmetric_list[pk][k]; 
			mnum =   nk['combined same, near, article'];
			mden = nk['combined same, near, article'] - ( nk['same and near sentence']) ;
			if(mden == 0){ mden = 1; }   ///TODO:  is this right?
			//console.log(mden);
			multiplier = mnum / mden;

			/* THIS IS WHERE I CALCULATE THE METRIC */  
			nweight = ( nk['same sentence'] + (near_co * (nk['same and near sentence'] - nk['same sentence'])) + (same_art_co * nk['same article'])) * multiplier; 
			nweight = nweight.toFixed(2);
			newmetric_list[pk][k]['weight'] = nweight;	
			nodeweights[pk].push([k,nweight]);
		});	
	}
	
	for( pk in nodeweights){ nodeweights[pk].sort(function(a, b) {return a[1] - b[1]}).reverse(); }

	//make ul printout for each entity type list and put them in combined view below
	//then if it looks good make things on main graph based on that!

	billout = ""; miscout = "";
	polout = "Politicians: <ul>"; nodeweights['pol'].forEach(function(d){ polout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	orgout = "Organizations: <ul>"; nodeweights['org'].forEach(function(d){ orgout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	perout = "Persons: <ul>"; nodeweights['per'].forEach(function(d){ perout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	locout = "Locations: <ul>"; nodeweights['loc'].forEach(function(d){ locout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; });
	if(Object.keys(op[5]).length > 0){ billout = "Bills: <ul>"; nodeweights['bill'].forEach(function(d){ billout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }
	if(Object.keys(op[6]).length > 0){ miscout = "Misc: <ul>"; nodeweights['misc'].forEach(function(d){ miscout += "<li class='res"+d[0]+"'><a href='javascript: clicknode("+d[0]+");'>"+graph2.elements.nodes[parseInt(d[0])].full_name+"</a> - "+d[1]+"</li>"; }); }

	out['new metric'] = [ polout, orgout, perout,locout,billout,miscout];
	matchtype = "new metric";
	output = "<table id='new_metric_results'><tr><td style='width:30%'><ul>";
	output += "<li><p style='color:rgba(31, 119, 180, .8); font-size:18px;'>"+centernode+" has most<br/>"+matchtype+" occurrences with</p></li>";
	output += "<li>Politician <a href='javascript: clicknode("+nodeweights['pol'][0][0]+");'>"+graph2.elements.nodes[nodeweights['pol'][0][0]]['full_name'] + "</a> - ("+nodeweights['pol'][0][1]+") </li>";
	output += "<li>Person  <a href='javascript: clicknode("+nodeweights['per'][0][0]+");'>"+graph2.elements.nodes[nodeweights['per'][0][0]]['full_name'] + "</a> - ("+ nodeweights['per'][0][1]+") </li>";
	output += "<li>Organization <a href='javascript: clicknode("+nodeweights['org'][0][0]+");'>"+graph2.elements.nodes[nodeweights['org'][0][0]]['full_name'] + "</a> - ("+nodeweights['org'][0][1]+")</li>";
	output += "<li>Location <a href='javascript: clicknode("+nodeweights['loc'][0][0]+");'>"+graph2.elements.nodes[nodeweights['loc'][0][0]]['full_name'] + "</a> - ("+nodeweights['loc'][0][1]+")</li>";
	if(billout.length > 0){ output += "<li>Bill <a href='javascript: clicknode("+nodeweights['bill'][0][0]+");'>"+graph2.elements.nodes[nodeweights['bill'][0][0]]['full_name'] + "</a> - ("+nodeweights['bill'][0][1]+")</li>";}
	output += "<li>Misc <a href='javascript: clicknode("+nodeweights['misc'][0][0]+");'>"+graph2.elements.nodes[nodeweights['misc'][0][0]]['full_name'] + "</a> - ("+nodeweights['misc'][0][1]+")</li></ul>";
	output += '</td><td style="width:70%; height:250px; padding-left:10px;"><canvas id="myChart'+4+'"></canvas></td></tr>';

	top_objs5 = output;
	colout5 = "<tr><td colspan=2><table class='innerres'><tr style='vertical-align:top'><td>"+polout+"</td><td>"+orgout+"</td><td>"+perout+"</td><td>"+locout+"</td><td>"+billout+"</td><td>"+miscout+"</td></tr></table></td></tr></table>";

	newout = {};  //just to remove some formatting to make more compact
	for(m in out){  
		newout[m] = [ out[m][0].replace("Politicians: <ul>","<ul>"), out[m][1].replace("Organizations: <ul>","<ul>"), out[m][2].replace("Persons: <ul>","<ul>"), out[m][3].replace("Locations: <ul>","<ul>"), out[m][4].replace("Bills: <ul>","<ul>"), out[m][5].replace("Misc: <ul>","<ul>")]; 
	}
	out = newout;


	combined = "<table id='combinedstats'>";
	combined += "<tr class='cstop'><td colspan=5 style='text-align: center'><a style='color:red' href=''>Politicians</a>&nbsp;&nbsp;<a href=''>Organizations</a>&nbsp;&nbsp;<a href=''>People</a>&nbsp;&nbsp;<a href=''>Locations</a>&nbsp;&nbsp;<a href=''>Bills</a>&nbsp;&nbsp;<a href=''>Misc</a>";
	combined += "<tr class='pol'><td style='font-weight: bold; font-size: 18px; text-align: center;' colspan=4>Top Politicians</td></tr><tr class='header pol'><td>same sent</td><td>same sent or near</td><td>same sent,near or same article</td><td>same article only</td><td>combined metric</td></tr>";
	combined += "<tr class='pol'><td>"+out['same sentence'][0]+"</td><td>"+out['same and near sentence'][0]+"</td><td>"+out['combined same, near, article'][0]+"</td><td>"+out['same article'][0]+"</td><td>"+out['new metric'][0]+"</td></tr>";
	combined += "<tr class='org'><td style='font-weight: bold; font-size: 18px; text-align: center;' colspan=4>Top Organizations</td></tr><tr class='header org'><td>same sent</td><td>same sent or near</td><td>same sent,near or same article</td><td>same article only</td><td>combined metric</td></tr>";
	combined += "<tr class='org'><td>"+out['same sentence'][1]+"</td><td>"+out['same and near sentence'][1]+"</td><td>"+out['combined same, near, article'][1]+"</td><td>"+out['same article'][1]+"</td><td>"+out['new metric'][1]+"</td></tr>";
	combined += "<tr class='per'><td style='font-weight: bold; font-size: 18px; text-align: center;' colspan=4>Top Persons</td></tr><tr class='header per'><td>same sent</td><td>same sent or near</td><td>same sent,near or same article</td><td>same article only</td><td>combined metric</td></tr>";
	combined += "<tr class='per'><td>"+out['same sentence'][2]+"</td><td>"+out['same and near sentence'][2]+"</td><td>"+out['combined same, near, article'][2]+"</td><td>"+out['same article'][2]+"</td><td>"+out['new metric'][2]+"</td></tr>";
	combined += "<tr class='loc'><td style='font-weight: bold; font-size: 18px; text-align: center;' colspan=4>Top Locations</td></tr><tr class='header loc'><td>same sent</td><td>same sent or near</td><td>same sent,near or same article</td><td>same article only</td><td>combined metric</td></tr>";
	combined += "<tr class='loc'><td>"+out['same sentence'][3]+"</td><td>"+out['same and near sentence'][3]+"</td><td>"+out['combined same, near, article'][3]+"</td><td>"+out['same article'][3]+"</td><td>"+out['new metric'][3]+"</td></tr>";
	combined += "<tr class='bill'><td style='font-weight: bold; font-size: 18px; text-align: center;' colspan=4>Top Bills</td></tr><tr class='header bill'><td>same sent</td><td>same sent or near</td><td>same sent,near or same article</td><td>same article only</td><td>combined metric</td></tr>";
	combined += "<tr class='bill'><td>"+out['same sentence'][4]+"</td><td>"+out['same and near sentence'][4]+"</td><td>"+out['combined same, near, article'][4]+"</td><td>"+out['same article'][4]+"</td><td>"+out['new metric'][4]+"</td></tr>";
	combined += "<tr class='misc'><td style='font-weight: bold; font-size: 18px; text-align: center;' colspan=4>Top Misc</td></tr><tr class='header misc'><td>same sent</td><td>same sent or near</td><td>same sent,near or same article</td><td>same article only</td><td>combined metric</td></tr>";
	combined += "<tr class='misc'><td>"+out['same sentence'][5]+"</td><td>"+out['same and near sentence'][5]+"</td><td>"+out['combined same, near, article'][5]+"</td><td>"+out['same article'][5]+"</td><td>"+out['new metric'][5]+"</td></tr>";
	combined += "</table>"; 

	//return stuff here now
	callback( [top_objs, colout, top_objs2, colout2, top_objs3, colout3, top_objs4, colout4, top_objs5, colout5, combined] );
}

function get_most_sentences_async(center_name,matchtype){

	nodetypes = graph2.elements.nodes.map(function(d){ 
			if( d['full_name']  != center_name ){ 
				curid = name_to_index[d['full_name']];  
				clinks = graph2.elements.links.filter(function(e){ return e['target'] == curid }); 
				tctypes = {}; 
				if( clinks.length > 0){
					clinks[0]['inst'].forEach(function(f){ if(f['type'] in tctypes){tctypes[f['type']].push(f);}else{ tctypes[f['type']] = [f];}});
				}
				return tctypes; 
			}
			else { return {}; }
		})
	if(matchtype == "same sentence"){ node_same = nodetypes.map(function(m){ if('same sentence' in m){ return m['same sentence'].length }else{ return 0; }}); }
	if(matchtype == "same article"){ node_same = nodetypes.map(function(m){ if('same article' in m){ return m['same article'].length }else{ return 0; }}); }
	if(matchtype == "same and near sentence"){ node_same = nodetypes.map(function(m){ 
			if('same sentence' in m && 'near' in m){	return m['same sentence'].length + m['near'].length; }
			else{
				if('same sentence' in m){	return m['same sentence'].length ; }
				else{
					if('near' in m){	return m['near'].length; }
					else{ return 0; }
				}
			}
		}); 
	}
	if(matchtype == "combined same, near, article"){ node_same = nodetypes.map(function(m){ 
			if ('same sentence' in m && 'near' in m && 'same article' in m){ return m['same sentence'].length + m['near'].length + m['same article'].length;}
			else{ 
				if('same article' in m){
					if('same article' in m && 'near' in m){	return m['same article'].length + m['near'].length; }
					else{
						if('same sentence' in m && 'same article' in m){	return m['same sentence'].length + m['same article'].length; }
						else{ return m['same article'].length; }
					}
				}
				else{
					if('same sentence' in m && 'near' in m){	return m['same sentence'].length + m['near'].length; }
					else{
						if('same sentence' in m){	return m['same sentence'].length ; }
						else{
							if('near' in m){	return m['near'].length; }
							else{ return 0; }
						}
					}
				}
			}
		}); 
	}

	polmaxind = -1; polmaxval = -1; permaxind = -1; permaxval = -1; locmaxind = -1; locmaxval = -1; 
	orgmaxind = -1; orgmaxval = -1; billmaxind = -1; billmaxval = -1; miscmaxind = -1; miscmaxval = -1; 

	polobj = {}; perobj = {}; locobj = {}; orgobj = {}; billobj = {}; miscobj = {};
	Object.keys(node_same).forEach(function(d){ 
		curtype = graph2.elements.nodes[d]['entity_type'];
		if( curtype == 'politician') { if(node_same[d] > polmaxval ){ polmaxind = d; polmaxval = node_same[d]; } if(node_same[d] > 0){polobj[d] = node_same[d];} }
		if( curtype == 'ORGANIZATION') { if(node_same[d] > orgmaxval ){ orgmaxind = d; orgmaxval = node_same[d]; } if(node_same[d] > 0){orgobj[d] = node_same[d];}}
		if( curtype == 'PERSON') { if(node_same[d] > permaxval ){ permaxind = d; permaxval = node_same[d]; } if(node_same[d] > 0){perobj[d] = node_same[d];}}
		if( curtype == 'LOCATION') { if(node_same[d] > locmaxval ){ locmaxind = d; locmaxval = node_same[d]; } if(node_same[d] > 0){locobj[d] = node_same[d];}}
		if( curtype == 'BILL') { if(node_same[d] > billmaxval ){ billmaxind = d; billmaxval = node_same[d]; } if(node_same[d] > 0){billobj[d] = node_same[d];}}
		if( curtype == 'MISC') { if(node_same[d] > miscmaxval ){ miscmaxind = d; miscmaxval = node_same[d]; } if(node_same[d] > 0){miscobj[d] = node_same[d];}}

	});

	if(matchtype == "same sentence"){ output = "<table id='same_sent_results'><tr><td style='width:30%'><ul>";}
	if(matchtype == "same article"){ output = "<table id='same_article_results'><tr><td style='width:30%'><ul>";}
	if(matchtype == "same and near sentence"){ output = "<table id='same_sent_and_near_results'><tr><td style='width:30%'><ul>";}
	if(matchtype == "combined same, near, article"){ output = "<table id='same_combined_results'><tr><td style='width:30%'><ul>";}
	output += "<li><p style='color:rgba(31, 119, 180, .8); font-size:18px;'>"+center_name+" has most<br/>"+matchtype+" occurrences with</p></li>";
	output += "<li>Politician <a href='javascript: clicknode("+polmaxind+");'>"+graph2.elements.nodes[polmaxind]['full_name'] + "</a> - ("+polmaxval+") </li>";
	output += "<li>Person  <a href='javascript: clicknode("+permaxind+");'>"+graph2.elements.nodes[permaxind]['full_name'] + "</a> - ("+ permaxval+") </li>";
	output += "<li>Organization <a href='javascript: clicknode("+orgmaxind+");'>"+graph2.elements.nodes[orgmaxind]['full_name'] + "</a> - ("+orgmaxval+")</li>";
	output += "<li>Location <a href='javascript: clicknode("+locmaxind+");'>"+graph2.elements.nodes[locmaxind]['full_name'] + "</a> - ("+locmaxval+")</li>";
	if(billmaxind > -1 ){output += "<li>Bill <a href='javascript: clicknode("+billmaxind+");'>"+graph2.elements.nodes[billmaxind]['full_name'] + "</a> - ("+billmaxval+")</li>"; }
	output += "<li>Misc <a href='javascript: clicknode("+miscmaxind+");'>"+graph2.elements.nodes[miscmaxind]['full_name'] + "</a> - ("+miscmaxval+")</li></ul>";
	if(matchtype == "same sentence"){ n = 0;}
	if(matchtype == "same article"){ n = 3;}
	if(matchtype == "same and near sentence"){ n = 1;}
	if(matchtype == "combined same, near, article"){ n = 2;}
	output += '</td><td style="width:70%; height:250px; padding-left:10px;"><canvas id="myChart'+n+'"></canvas></td></tr>';

	return [output ,polobj,orgobj,perobj,locobj,billobj,miscobj];
}
