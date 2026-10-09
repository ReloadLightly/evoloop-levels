/* Original research stepping kernel. CTRBL, synchronous, periodic boundaries. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void advance(uint8_t *grid, uint8_t *labels, const uint8_t *lut,
             int h, int w, int steps) {
    size_t n = (size_t)h*w;
    uint8_t *next = malloc(n), *nl = labels ? malloc(n) : NULL;
    if (!next || (labels && !nl)) abort();
    for (int t=0; t<steps; t++) {
        for (int y=0; y<h; y++) for (int x=0; x<w; x++) {
            int p=y*w+x, a=(y ? y-1 : h-1)*w+x,
                b=y*w+(x+1==w ? 0 : x+1),
                c=(y+1==h ? 0 : y+1)*w+x,
                d=y*w+(x ? x-1 : w-1);
            int k=((((grid[p]*9+grid[a])*9+grid[b])*9+grid[c])*9+grid[d]);
            next[p]=lut[k];
            if (labels) nl[p]=next[p] ?
                ((grid[p] ? labels[p] : 0) | (grid[a] ? labels[a] : 0) |
                 (grid[b] ? labels[b] : 0) | (grid[c] ? labels[c] : 0) |
                 (grid[d] ? labels[d] : 0)) : 0;
        }
        memcpy(grid,next,n);
        if (labels) memcpy(labels,nl,n);
    }
    free(next); free(nl);
}
