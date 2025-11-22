#include <stdlib.h>
#include <limits.h>

void *mymalloc( size_t size ) {
  void *s;
  if ( (s=malloc(size)) == NULL ) {
  	printf("\nERRO memoria");
    fprintf( stderr, "malloc : Not enough memory.\n" );
    exit( EXIT_FAILURE );
  }
  //printf("\nMALLOC");
  //fflush(stdout);
  return s;
}

void error_reading_file(char *text){
  printf("%s\n", text);
  exit( EXIT_FAILURE );
}

/*************** L'Ecuyer random number generator ***************/
double rando()
 {
  static int x10 = 12345, x11 = 67890, x12 = 13579, /* initial value*/
             x20 = 24680, x21 = 98765, x22 = 43210; /* of seeds*/
  const int m = 2147483647; const int m2 = 2145483479; 
  const int a12= 63308; const int q12=33921; const int r12=12979; 
  const int a13=-183326; const int q13=11714; const int r13=2883; 
  const int a21= 86098; const int q21=24919; const int r21= 7417; 
  const int a23=-539608; const int q23= 3976; const int r23=2071;
  const double invm = 4.656612873077393e-10;
  int h, p12, p13, p21, p23;
  h = x10/q13; p13 = -a13*(x10-h*q13)-h*r13;
  h = x11/q12; p12 = a12*(x11-h*q12)-h*r12;
  if (p13 < 0) p13 = p13 + m; if (p12 < 0) p12 = p12 + m;
  x10 = x11; x11 = x12; x12 = p12-p13; if (x12 < 0) x12 = x12 + m;
  h = x20/q23; p23 = -a23*(x20-h*q23)-h*r23;
  h = x22/q21; p21 = a21*(x22-h*q21)-h*r21;
  if (p23 < 0) p23 = p23 + m2; if (p21 < 0) p21 = p21 + m2;
  x20 = x21; x21 = x22; x22 = p21-p23; if(x22 < 0) x22 = x22 + m2;
  if (x12 < x22) h = x12 - x22 + m; else h = x12 - x22;
  if (h == 0) return(1.0); else return(h*invm);
 }

/*********** return an integer between low and high *************/
int unif(int low, int high)
 {return low + (int)((double)(high - low + 1) * rando()) ;}
/*******************************************************/
