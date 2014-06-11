#include<stdio.h>
#include<termios.h>
#include<unistd.h>
#include<sys/select.h>
#include<sys/time.h>

#include "kb.h"


/* kbhit()
 * Non-blocking keypress detector
 * returns 1 if at least one character waiting for input
 * returns 0 otherwise.
 */
int kb_hit()
{
    struct timeval tv;
    fd_set fds;
    tv.tv_sec = 0;
    tv.tv_usec = 0;
    FD_ZERO(&fds);
    FD_SET(STDIN_FILENO, &fds);
    select(STDIN_FILENO+1, &fds, NULL, NULL, &tv);
    return FD_ISSET(STDIN_FILENO, &fds);
}

/* nonblock(state)
 * Turn off/on nonblocking (canonical) state in
 * the controlling terminal (stdin)
 * state == 1 turns off canonical mode ==> non-blocking
 */
void kb_nonblock(int state)
{
    struct termios ttystate;

    //get the terminal state
    tcgetattr(STDIN_FILENO, &ttystate);

    if (state) {
      //turn off canonical mode
      ttystate.c_lflag &= ~ICANON;
      //minimum of number input read.
      ttystate.c_cc[VMIN] = 1; 
      }
    else {
      //turn on canonical mode
      ttystate.c_lflag |= ICANON;
      }
    //set the terminal attributes.
    tcsetattr(STDIN_FILENO, TCSANOW, &ttystate);
}

/* getch()
 * Get a character from the keyboard, if available.
 * returns char as int, 0 if none available.
 */
int kb_getch()
{
  int c=0;
  if(kb_hit()) {
    c = getchar();
    }
  return(c);
}
