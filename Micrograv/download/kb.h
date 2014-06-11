#ifndef UGRAV_DOWNLOAD_KB
#define UGRAV_DOWNLOAD_KB

/* kbhit()
 * Non-blocking keypress detector
 * returns 1 if at least one character waiting for input
 * returns 0 otherwise.
 */
int kb_hit();
/* nonblock(state)
 * Turn off/on nonblocking (canonical) state in
 * the controlling terminal (stdin)
 * state == 1 turns off canonical mode ==> non-blocking
 */
void kb_nonblock(int state);
/* getch()
 * Get a character from the keyboard, if available.
 * returns char as int, 0 if none available.
 */
int kb_getch();

#endif
