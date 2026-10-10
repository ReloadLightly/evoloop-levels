/* Equivalent synchronous CTRBL dynamics. Quiescent tiles are skipped only
   outside the occupied-tile von Neumann halo; LUT[00000] must equal zero. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define SIDE 16
void tiled_advance(uint8_t *grid,uint8_t *labels,const uint8_t *lut,int h,int w,int steps) {
    if(lut[0]!=0) abort();
    size_t n=(size_t)h*w;
    int ny=(h+SIDE-1)/SIDE,nx=(w+SIDE-1)/SIDE,nt=ny*nx;
    uint8_t *next=calloc(n,1),*nl=labels?calloc(n,1):NULL;
    uint8_t *occupied=calloc(nt,1),*future=calloc(nt,1);
    if(!next || (labels&&!nl) || !occupied || !future) abort();
    for(int y=0;y<h;y++)for(int x=0;x<w;x++)if(grid[y*w+x])occupied[(y/SIDE)*nx+x/SIDE]=1;
    for(int t=0;t<steps;t++){
        memset(next,0,n);if(labels)memset(nl,0,n);memset(future,0,nt);
        for(int ty=0;ty<ny;ty++)for(int tx=0;tx<nx;tx++){
            int tile=ty*nx+tx;
            int up=(ty?ty-1:ny-1)*nx+tx,down=(ty+1==ny?0:ty+1)*nx+tx;
            int left=ty*nx+(tx?tx-1:nx-1),right=ty*nx+(tx+1==nx?0:tx+1);
            if(!(occupied[tile]||occupied[up]||occupied[down]||occupied[left]||occupied[right]))continue;
            int yend=(ty+1)*SIDE<h?(ty+1)*SIDE:h,xend=(tx+1)*SIDE<w?(tx+1)*SIDE:w;
            for(int y=ty*SIDE;y<yend;y++)for(int x=tx*SIDE;x<xend;x++){
                int p=y*w+x,a=(y?y-1:h-1)*w+x,b=y*w+(x+1==w?0:x+1);
                int c=(y+1==h?0:y+1)*w+x,d=y*w+(x?x-1:w-1);
                int k=((((grid[p]*9+grid[a])*9+grid[b])*9+grid[c])*9+grid[d]);
                uint8_t v=lut[k];next[p]=v;if(v)future[tile]=1;
                if(labels)nl[p]=v?((grid[p]?labels[p]:0)|(grid[a]?labels[a]:0)|(grid[b]?labels[b]:0)|(grid[c]?labels[c]:0)|(grid[d]?labels[d]:0)):0;
            }
        }
        memcpy(grid,next,n);if(labels)memcpy(labels,nl,n);memcpy(occupied,future,nt);
    }
    free(next);free(nl);free(occupied);free(future);
}
