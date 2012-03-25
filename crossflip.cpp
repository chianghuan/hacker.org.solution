#include <cstdio>
#include <cstring>

#define MAXS 400
#define MAXB 160000
#define BL 64
typedef long long lint;

char buffer[MAXB];
lint mask[BL];

int nonz[100000], tail;

struct equat
{
    lint *bits; // set of BL bits
    int v; // rhs vector elem
    int c; // count of the non-zero bitsets
    // 
    equat() : bits(NULL), v(0), c(0) {}
    // init
    inline void init(int _v, int bitc)
    {
        v = _v;
        bits = new lint[bitc / BL + 1];
        memset(bits, 0, sizeof(lint) * (bitc/BL+1));
    }
    // setbit
    inline void setbit(int bitc)
    {
        bits[bitc/BL] |= mask[bitc%BL];
    }
    // getbit
    inline char getbit(int bitc)
    {
        int n = bitc/BL;
        if (bits[n])
            return (bits[n] & mask[bitc%BL]) ? '1' : '0';
        return '0';
    }
    // xor
    inline void xo(const equat &other, int blen)
    {
        v ^= other.v;
        for (int i = 0; i < tail; i++)
        {
            int j = nonz[i];
            if (other.bits[j]) // only ^ when non-zero
            {
                if (bits[j]) // when non-zero, ^
                {
                    bits[j] ^= other.bits[j];
                    if (!bits[j]) c--; // if zero, count-1
                }
                else // zero, just assign the non-zero from other
                {
                    bits[j] = other.bits[j];
                    c++; // count+1
                }
            }
        }
    }
    // one bit
    inline void one(int blen)
    {
        bool find = false;
        for (int i = blen-1; i > -1; i--)
            if (find and bits[i])
            {
                bits[i] = (lint)(0);
                continue;
            }
            else if (bits[i]) 
            {
                find = true;
                while (bits[i] & bits[i]-1)
                {
                    bits[i] &= bits[i] - 1;
                }
            }
    }
    // count bit
    int count(int blen)
    {
        c = 0;
        for (int i = 0; i < blen; i++)
        {
            if (bits[i]) c++;
        }
        return c;
    }
    // dump 
    void dump(int blen)
    {
        lint mask = (lint)(1)<<(BL-1);
        for (int i = blen-1; i > -1; i--)
        {
            lint t = bits[i];
            for (int j = 0; j < BL; j++)
            {
                if (t & mask) printf("1");
                else printf("0");
                t<<=1;
            }
        }
        printf("  %d\n", v);
    }
    ~equat()
    {
        if (bits) delete bits;
    }
};

equat *eqs;

void calcnz(int k, int blen)
{
    tail = 0;
    for (int i = 0; i < blen; i++)
    {
        if (eqs[k].bits[i])
            nonz[tail++] = i;
    }
}

int gauss(int len, int blen)
{ 
    // delta
    int *sel = new int[len];
    for (int i = 0; i < len; i++)
        sel[i] = -1;
    equat temp;
    for (int k = 0; k < len; k++)
    {
        int mnc = 10000000; // big enough for lvl with 10000000*64 
        int pos = -1;
        bool find = false;
        for (int i = 0; i < len; i++)
        {
            if (sel[i] == -1 && eqs[i].getbit(len-k-1) != '0')
            {
                if (eqs[i].c < mnc)
                {
                    mnc = eqs[i].c;
                    find = true;
                    pos = i;
                }
            }
        }
        if (find)
        {
            sel[k] = pos;
            temp = eqs[pos];
            eqs[pos] = eqs[k];
            eqs[k] = temp;
        }
        else
        {
            continue;
        }
        calcnz(k, blen);
        for (int i = 0; i < len; i++)
        {
            if (sel[i] == -1 && eqs[i].getbit(len-k-1) != '0' && i!=k)
            {
                eqs[i].xo(eqs[k], blen);
            }
        }
    }
    // elim
    for (int k = len-1; k > -1; k--)
    {
        calcnz(k, blen);
        if (eqs[k].getbit(len-k-1) != 0)
        {
            for (int i = k-1; i > -1; i--)
            {
                if (eqs[i].getbit(len-k-1) != '0')
                { 
                    eqs[i].xo(eqs[k], blen);
                }
            }
        }
    }
    for (int i = 0; i < len; i++)
    {
        eqs[i].one(blen);
    }
    // don't forget temp
    temp.init(0, len);
    for (int i = 0; i < len; i++)
    {
        if (eqs[i].v)
        {
            calcnz(i, blen);
            temp.xo(eqs[i], blen);
        }
    }
    for (int i = len - 1; i > -1; i--)
    {
        buffer[len - i - 1] = temp.getbit(i);
    }
    buffer[len] = '\0';
    return 0;
}

char board[MAXS][MAXS];
int proj[MAXB], projb[MAXB];

int preproc()
{
    FILE *file = fopen("crossinput.txt", "r");
    int h, w, sz; 
    fscanf(file, "%d", &h);
    for (int i = 0; i < h; i++)
    {
        fscanf(file, "%s", board[i]);
    }
    w = strlen(board[0]);
    sz = h * w;
    fclose(file);

    int block = 0;
    for (int i = 0, num = 0; i < sz; i++)
    {
        if (board[i/w][i%w] != '2')
        {
            proj[i] = num;
            projb[num] = i;
            num++;
        }
        else block++;
    }

    int len = sz - block;
    eqs = new equat[len];
    for (int i = 0; i < len; i++)
    {
        eqs[i].init(0, len);
    }
    // set rhs
    for (int i = 0; i < sz; i++)
    {
        if (board[i/w][i%w] == '1')
            eqs[proj[i]].v = 1;
    }
    // init eqs
    for (int i = 0; i < sz; i++)
    {
        int x = i/w, y = i%w;
        if (board[x][y] == '2') continue;
        // 4 directions
        for (int j = x; j < h; j++)
        {
            if (board[j][y] == '2') break;
            eqs[proj[i]].setbit(len - 1 - proj[j*w+y]);
        }
        for (int j = x-1; j > -1; j--)
        {
            if (board[j][y] == '2') break;
            eqs[proj[i]].setbit(len - 1 - proj[j*w+y]);
        }
        for (int j = y; j < w; j++)
        {
            if (board[x][j] == '2') break;
            eqs[proj[i]].setbit(len - 1 - proj[x*w+j]);
        }
        for (int j = y-1; j > -1; j--)
        {
            if (board[x][j] == '2') break;
            eqs[proj[i]].setbit(len - 1 - proj[x*w+j]);
        }
    }

    return len;
}

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        printf("This won't work with itself.\n");
        printf("Run crossflip-cpp.py instead.\n");
        return 0;
    }
    for (int i = 0; i < BL; i++)
    {
        lint b = 1;
        mask[i] = (b << i);
    }

    int len, v, blen;

    /* preprocess */
    len = preproc();

    blen = len/BL+1;
    printf("matrix size: %d\n", len);

    /* core algor */
    gauss(len, blen);
    
    FILE *f = fopen("crossoutput.txt", "w+");
    fprintf(f, "%s", buffer);
    fclose(f);
    return 0;
}
