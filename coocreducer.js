function(ngramid, coocslices) {
    var totalcooc = { totaldegre: 0, latest :null };
    //for (var i=0; i<coocslices.length; i++) {
        coocslices.forEach(function(slice){

            for (var neighbourid in slice) {
                if ( neighbourid in totalcooc ) {
                    totalcooc[neighbourid] += slice[neighbourid];
                } else {
                    totalcooc[neighbourid] = slice[neighbourid];
                    totalcooc.totaldegre += 1;
                    totalcooc.latest = { neighbourid: slice[neighbourid] };
                }  
            }
            
        });

    //}
    return totalcooc;
};