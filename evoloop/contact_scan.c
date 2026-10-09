/* Read-only compiled equivalent of evoloop.tracking.contact, no CA stepping. */
#include <stdint.h>
int contact_scan(const uint8_t *g,const uint8_t *lab,int h,int w) {
    for (int y=0;y<h;y++) for (int x=0;x<w;x++) {
        int p=y*w+x;
        if (!g[p]) continue;
        if (lab[p]==3) return 1;
        if (lab[p]!=1 && lab[p]!=2) continue;
        int r=y*w+(x+1==w ? 0 : x+1),b=(y+1==h ? 0 : y+1)*w+x;
        if (g[r] && ((lab[p]==1 && lab[r]==2) || (lab[p]==2 && lab[r]==1))) return 1;
        if (g[b] && ((lab[p]==1 && lab[b]==2) || (lab[p]==2 && lab[b]==1))) return 1;
    }
    return 0;
}
