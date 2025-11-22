# Makefile 

PACKAGE = lsscp
SRCS    = $(PACKAGE).c
# HEADS = $(PACKAGE).h
OBJS    = $(SRCS:.c=.o)

FILES   = $(SRCS) utils.c scp42.txt
VER     = `date +%Y%m%d`

### command and flags ###
# uncomment when debugging
#DEBUG  = -ggdb -pg # -lefence

# common (*.o)
LD      = gcc
LDFLAGS = -g $(DEBUG)
LDLIBS  = -lm

# C (*.c)
CC      = gcc
CFLAGS  = -g -O2 -Wall $(DEBUG)
CPPFLAGS= -I.

# command
#RM = rm

### rules ###
.SUFFIXES:
.SUFFIXES: .o .c .cc .f .p

all: $(PACKAGE)

$(PACKAGE): $(OBJS)
	$(LD) $(LDFLAGS) $(LDLIBS) $(OBJS) -o $@

$(OBJS): $(HEADS) Makefile

.c.o:
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

### useful commands ###

clean:
	$(RM) $(PACKAGE) $(OBJS)
	$(RM) *~ #*#

tar:
	@echo $(PACKAGE)-$(VER) > .package
	@$(RM) -r `cat .package`
	@mkdir `cat .package`
	@ln $(FILES) `cat .package`
	tar cvf - `cat .package` | gzip -9 > `cat .package`.tar.gz
	@$(RM) -r `cat .package` .package

zip:
	zip -9 $(PACKAGE)-$(VER).zip $(FILES)


prof: run
	$(PROF) $(PACKAGE) | less

run: all
	./$(PACKAGE) --instance scp42.txt --ch1

