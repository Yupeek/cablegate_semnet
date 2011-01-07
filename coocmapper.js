function() {
    for (var ngramid in this.edges.NGram) {
        var coocslice = {};
        for (var neighbourid in this.edges.NGram[ngramid]) {
            // diagonal stores occurences
            coocslice[neighbourid] = 1;
        }
        emit(ngramid, coocslice);
    }
};