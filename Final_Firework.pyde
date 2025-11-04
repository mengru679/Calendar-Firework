
from datetime import date, datetime as _dt
import calendar, sys, os, time

# ---------- Settings Canvas & Calendar ----------
CANVAS_W, CANVAS_H = 1400, 800                         # Overall size settings
CAL_SCALE = 0.70                                       # Control the overall calendar size
LEFT_MARGIN = 20                                       # Left offset for alignment of calendar grid
BOTTOM_MARGIN = 36                                     # Control the border

CELL_W, CELL_H = int(90*CAL_SCALE), int(58*CAL_SCALE)  # Size of each date cell
HEADER_H = int(58*CAL_SCALE)                           # Height of header section

# ---------- Grid origin (bottom-left layout) ----------
CAL_X = LEFT_MARGIN
CAL_Y = CANVAS_H - BOTTOM_MARGIN - 6*CELL_H

# ---------- Define weekday and month name lists for labeling purposes ----------
WEEK_EN = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
MONTH_EN = ["","January","February","March","April","May","June",
            "July","August","September","October","November","December"]

# ---------- Modes ----------
display_mode = "text"  # "text" or "shape"  

# ---------- Open macOS Calendar ----------
_MAC_REF_UNIX = 978307200
def _mac_secs(y,m,d):
    t = _dt(y, m, d, 12, 0, 0)
    return int(time.mktime(t.timetuple())) - _MAC_REF_UNIX

def open_native_calendar(y,m,d):
    if sys.platform == "darwin":
        os.system('open "calshow:%d"' % _mac_secs(y,m,d))

# ---------- Fireworks ----------
TEXT_STRING = "HELLO"    # Default text
TEXT_SIZE = 180          # The size of the text particle
SAMPLE_STEP = 10         # The density of text particles
PTS_PER_FRAME = 40       # The number of emissions per frame
GRAV = 0.18              # The intensity of the fireworks as they fall
FADE = 3.0               # The speed at which the fireworks fade out
TRAIL = 26               # Adjusts how slowly the fireworks trails disappear
CLICK_V = (-6, 5, -20, -15)  # The range of the fireworks when the mouse is clicked

# Editable sizes for Jan 1 two-line text:
HAPPY_TOP_SIZE = 100      # "HAPPY" (top line)
HAPPY_BOTTOM_SIZE = 100   # "NEW YEAR" (bottom line)

# --------- Particle Class ---------
# Each particle is one small dot of the firework.
class Particle:
    def __init__(self, p, v, col, size=3, life=255):  
        # Starting position, speed, and acceleration
        self.pos = p.get();      # Position
        self.vel = v.get();      # Velocity
        self.acc = PVector(0,0)  # Acceleration (used for gravity)
        self.col = col;          # Color
        self.size = size;        # Size of the dot
        self.life = life         # How long it stays visible     
    def apply(self, f): self.acc.add(f)

# Update movement each firework frame:
    def update(self):
        self.vel.mult(0.985);    # Small slowdown
        self.vel.add(self.acc);  # Apply acceleration
        self.pos.add(self.vel)   # Update porition
        self.acc.mult(0);        # Reset
        self.life -= FADE        # Fade out over time

# Check if the firework particle has faded away
    def done(self): return self.life <= 0
    def show(self):
        noStroke(); fill(self.col, map(self.life,0,255,0,255))  # Fade with time
        ellipse(self.pos.x, self.pos.y, self.size, self.size)

class Burst:
    def __init__(self,x,y,h):
        self.ps=[]              # A list of all firework particles in this burst
        n = int(random(22,48))  # Number of particles in one explosion
        for _ in range(n):      # Give each particle a random direction and speed
            a = random(TWO_PI); 
            s = random(1.2,5.2)*random(0.25,1.0)
            v = PVector(cos(a)*s, sin(a)*s)
        
        # Give each particle a slightly different color and brightness
            col = color((h+random(-40,40))%360, random(70,100), random(85,100))
        # Create and add the particle to the list
            self.ps.append(Particle(PVector(x,y), v, col, size=random(1.5,3), life=random(240,320)))
    
    def apply(self,f):                      # Add a force (like gravity) to every firework particle
        for p in self.ps: p.apply(f)
    def update(self):                       # Update each firework particle’s position and remove the ones that have faded
        for p in self.ps: p.update()
        self.ps=[p for p in self.ps if not p.done()]
    def show(self):                         # Draw all the firework particles in this burst
        for p in self.ps: p.show()
    def done(self): return len(self.ps)==0  # Check if all particles are gone

# --------- lists to hold different firework elements ---------
text_pts=[];  # Stores the points that make up text shapes
bursts=[];    # Stores all active explosions or burst effects
rockets=[]    # Stores all rockets currently flying on screen

special_after_text = None     # Used to show special text after a shape animation 
special_delay_frames = 30     # Delay before switching to the next
shape_done_frame = -1         # Records the frame when a shape animation finishes

# ---------- Draw a ring of fireworks ----------
def ring(x,y,r,n,h):             # Creates a circular ring of small firework bursts.
    for i in range(n):
        a=TWO_PI*i/n; bursts.append(Burst(x+cos(a)*r, y+sin(a)*r, h))

# ---------- Generate points from text ----------
def gen_text_points(s):
    global text_pts
    text_pts=[]
    pg=createGraphics(width,height)    # Create a canvas to draw the text first
    pg.beginDraw()
    pg.colorMode(HSB,360,100,100,255)
    pg.background(0)
    pg.fill(0,0,100)
    pg.textAlign(CENTER,CENTER)

    lines = s.split("\n")                               # Split text into lines(Like "HAPPY NEW YEAR)

    if len(lines) == 1:                                 # Different situations, different positions
        pg.textSize(TEXT_SIZE)
        pg.text(lines[0], width/4, height/3 - 90)
    else:
        top_text = lines[0]                             # If it’s multi-line text
        bottom_text = "\n".join(lines[1:])              # Merge the rest as the second line

        top_size = HAPPY_TOP_SIZE
        bottom_size = HAPPY_BOTTOM_SIZE
        line_gap_k = 1.10                               # line spacing factor

        total_h = top_size + bottom_size * line_gap_k   # Calculate total height so the two lines stay nicely centered
        start_y = height * 0.2- total_h / 2.0  

        # Happy line
        pg.textSize(top_size)
        pg.text(top_text, width/3 - 100, start_y + top_size * 0.5)

        # New Year line
        pg.textSize(bottom_size)
        pg.text(bottom_text, width/3 - 100, start_y + top_size + bottom_size * 0.5 * line_gap_k)

    pg.endDraw()

# --------- Turn the drawn text into coordinate points ---------
    base=random(360)                        # random color hue base
    for y in range(0,height,SAMPLE_STEP):
        for x in range(0,width,SAMPLE_STEP):
            c=pg.get(x,y)
            if brightness(c)>50:

                jx=x+random(-SAMPLE_STEP*0.35,SAMPLE_STEP*0.35)    # Add random small jitter for natural look
                jy=y+random(-SAMPLE_STEP*0.35,SAMPLE_STEP*0.35)
                hue=(base+map(jx,0,width,-30,30))%360              # Create hue variation
                text_pts.append((jx,jy,hue))                       # Save the point (x, y, color)

# ---------- Holiday shapes ----------
def spawn_shape_star(cx, cy, base_hue, scale=180, points=160):
    # Make a 5-point star shape
    outer, inner = 1.0, 0.45
    verts = []
    for k in range(10):
        r = outer if k % 2 == 0 else inner           # Alternate long and short points
        a = -HALF_PI + k * TWO_PI / 10.0             # Angle for each point
        verts.append(PVector(r*cos(a), r*sin(a)))
    
    samples = []                                     # Add dots along the edges of the star
    for i in range(len(verts)):
        a = verts[i]
        b = verts[(i+1) % len(verts)]
        steps = max(2, int(points / len(verts)))
        for s in range(steps):
            t = float(s)/steps
            samples.append(PVector(lerp(a.x,b.x,t), lerp(a.y,b.y,t)))
    
    for v in samples:                                # Add bursts around the star outline
        x = cx + v.x * scale
        y = cy + v.y * scale
        bursts.append(Burst(x, y, base_hue))

def spawn_shape_star_gold(cx, cy):
    base_h = 52                                      # Golden color
    spawn_shape_star(cx, cy, base_h, scale=210, points=260)

def xmas_tree(cx,cy):
    base=120;                               # Main color
    scale=320;                              # Overall tree size
    rows=8                                  # Number of tree levels
    
    for r in range(1, rows+1):              # Draw the green tree layers
        wf=float(r)/rows                    # How wide each layer should be
        y=cy - scale*0.8 + r*(scale/rows)   # Vertical position of each layer
        halfw=scale*0.6*wf                  # Half width of each layer
        cnt=int(10+4*r)                     # How many firework particles per row
        for k in range(cnt):                # Place bursts (small fireworks) in each tree layer
            x=map(k,0,cnt-1,cx-halfw,cx+halfw)
            bursts.append(Burst(x,y, base))
   
    for yy in range(int(cy+scale*0.18), int(cy+scale*0.55), 20):     # Draw the trunk
      for xx in range(int(cx-scale*0.09), int(cx+scale*0.09), 18):
        bursts.append(Burst(xx, yy, (base+20)%360))
        
    gold=48                         # Add a golden star on top
    for i in range(10):
        a=-HALF_PI + i*TWO_PI/10.0
        r = 80 if i%2==0 else 36    # Alternate long and short points
        bursts.append(Burst(cx + cos(a) * r, cy - scale * 0.83 + sin(a) * r, gold))
        
def valentine_heart(cx, cy, base_hue=350, scale=16, outline_points=220):
    for i in range(outline_points):                           # Draw the heart outline
        t = i * TWO_PI / outline_points                       # Move around the circle (0 to 2π)
        x = 16 * (sin(t) ** 3)                                # X formula for a heart curve
        y = 13*cos(t) - 5*cos(2*t) - 2*cos(3*t) - cos(4*t)    # Y formula for the curve
        px = cx + x * scale                                   # Scale and move the shape to center
        py = cy - y * scale                                   # Flip vertically (Processing’s Y is downward)
        bursts.append(Burst(px, py, base_hue))                # Add firework particle at each outline point

def newyear_rings(cx,cy):                                     # Draw four ring fireworks for the New Year
    for r,h in ((220,0),(170,360),(120,220),(80,40)):         # Each pair (r, h) means ring size and color
        ring(cx,cy,r,28,(h%360))                              # Draw a circle made of small firework

def play_shape(key):                                          # Play different holiday firework shapes
    cx,cy=width/2, height/2                                   # Center position on screen
    if key=="christmas":
        xmas_tree(cx,cy)
    elif key=="star":              
        spawn_shape_star_gold(cx,cy)
    elif key=="newyear":
        newyear_rings(cx,cy)
    elif key=="valentine":  
        valentine_heart(cx, cy)


# ---------- Holidays ----------
HOLIDAYS = {
    (1, 1):   ("New Year's Day", "newyear"),                   # Jan 1 play "newyear" shape
    (2, 14):  ("Valentine's Day", "valentine"),                # Feb 14 play "valentine" heart
    (12, 24): ("Christmas Eve",  "star"),                      # Dec 24 play star
    (12, 25): ("Christmas Day",  "christmas"),                 # Dec 25 play tree
}

# ---------- Date mapping ----------
today = date.today()
curY, curM = today.year, today.month
selectedD = -1                                                 # Which day user clicked

def cfg_for(m,d):
    if (m,d) in HOLIDAYS:
        name,key = HOLIDAYS[(m,d)]
        return {"display":"shape","key":key,"label":name}      # Show a shape
    return {"display":"text","text":"%02d-%02d"%(m,d)}         # Default: just show text date

def apply_pick(m,d):                                           # Handle user picking a calendar day
    global display_mode, TEXT_STRING, selectedD
    global special_after_text, shape_done_frame

    selectedD=d                                                # Clear screen and all running effects
    bursts[:]=[]; rockets[:]=[]; text_pts[:]=[]; background(0)
    open_native_calendar(curY,m,d)                             # Open the calendar on this date

    c = cfg_for(m,d)
    special_after_text = None                                  # Reset follow-up state
    shape_done_frame = -1

    if c["display"]=="shape":
        display_mode="shape"; play_shape(c["key"])             # After New Year rings finish, show "Happy new year"
        if (m, d) == (1, 1):
            special_after_text = "HAPPY\nNEW YEAR"
    else:
        display_mode="text"; TEXT_STRING=c["text"]; gen_text_points(TEXT_STRING)

# ---------- Calendar drawing (HEADER ON TOP) ----------
def month_title(y,m): return "%s %d"%(MONTH_EN[m], y)       # Show the month and year text on top

prev_rect = (0,0,0,0)                                       # Button rectangles
next_rect = (0,0,0,0)
def draw_calendar():
    global prev_rect, next_rect

    fill(0,0,100,230); noStroke()                           # Top header bar
    rect(0, 0, width, HEADER_H)                             # Draw header background
    fill(0); textAlign(CENTER,CENTER); textSize(int(24*CAL_SCALE))
    text(month_title(curY,curM), width/2, HEADER_H/2)       # Show month and year

    btnW,btnH = int(80*CAL_SCALE), int(32*CAL_SCALE)        # Prev / Next buttons
    prev_rect = (LEFT_MARGIN, (HEADER_H-btnH)//2, btnW, btnH)
    next_rect = (width-LEFT_MARGIN-btnW, (HEADER_H-btnH)//2, btnW, btnH)

    for (x,y,w,h,label) in (prev_rect+("Prev",), next_rect+("Next",)):        # Draw the two buttons and highlight when hovered
        fill(0,0,94 if (x<=mouseX<=x+w and y<=mouseY<=y+h) else 96)
        stroke(0,0,70); rect(x,y,w,h,8); noStroke()
        fill(0); textAlign(CENTER,CENTER); textSize(int(16*CAL_SCALE)); text(label, x+w/2, y+h/2)

    textSize(int(16*CAL_SCALE)); fill(0)                    # Weekday titles above the grid
    for i,wd in enumerate(WEEK_EN):
        textAlign(CENTER,CENTER)
        text(wd, CAL_X+i*CELL_W + CELL_W/2, CAL_Y - int(26*CAL_SCALE))

    first_wd, daysInMonth = calendar.monthrange(curY, curM)  # Calendar grid
    offset = first_wd
    isThisMonth = (today.year==curY and today.month==curM)
    day=1
    for r in range(6):
        for c in range(7):
            gx = CAL_X + c*CELL_W
            gy = CAL_Y + r*CELL_H
            idx = r*7+c
            inside = (idx>=offset and day<=daysInMonth)
            noStroke()
            if inside:
                if isThisMonth and day==today.day: fill(60,10,100)     # Highlight today
                else: fill(0,0,100)
                rect(gx,gy,CELL_W-1,CELL_H-1)
                if day==selectedD: fill(210,60,100,70); rect(gx,gy,CELL_W-1,CELL_H-1)  # Highlight selected day
            else:
                fill(0,0,96); rect(gx,gy,CELL_W-1,CELL_H-1)
            noFill(); stroke(0,0,82);                                  # Cell border
            rect(gx,gy,CELL_W-1,CELL_H-1)

            if inside:                                                 # Draw day number
                fill(0); textAlign(LEFT,TOP); textSize(int(18*CAL_SCALE))
                text(str(day), gx+int(8*CAL_SCALE), gy+int(6*CAL_SCALE))
                # two-line holiday label (split last word)
                if (curM,day) in HOLIDAYS:                             # Draw holiday labels
                    raw = HOLIDAYS[(curM,day)][0]
                    parts = raw.split()
                    label = " ".join(parts[:-1])+"\n"+parts[-1] if len(parts)>=2 else raw
                    pad = int(6*CAL_SCALE)
                    fill(210,80,100); textAlign(LEFT,BOTTOM); textSize(max(10,int(12*CAL_SCALE)))
                    textLeading(int(14*CAL_SCALE))
                    text(label, gx+pad, gy+CELL_H-pad)
                day += 1

# ---------- Processing lifecycle ----------
def setup():
    global special_after_text, shape_done_frame, display_mode, TEXT_STRING
    size(CANVAS_W, CANVAS_H)                                                   # Create the window
    colorMode(HSB,360,100,100,255); smooth();                                  # Use HSB colors, turn on anti-aliasing
    frameRate(60); background(0)                                               # 60 FPS, clear screen to black
    c = cfg_for(today.month, today.day)                                        # Get what to show for today's date

    special_after_text = None                                                  # Reset the follow-up (post-shape) text state
    shape_done_frame = -1

    if c["display"]=="shape":                                                  # Start in shape mode
        display_mode="shape"; 
        play_shape(c["key"])                                                   # Spawn the holiday pattern fireworks
        if (today.month, today.day) == (1, 1):                                 # Special behavior on Jan 1
            special_after_text = "HAPPY\nNEW YEAR"                             # After shape ends, show this text
    else:
        display_mode="text"; TEXT_STRING=c["text"]; gen_text_points(TEXT_STRING)

def draw():
    global special_after_text, shape_done_frame, display_mode, TEXT_STRING
    noStroke(); fill(0,0,90,TRAIL); rect(0,0,width,height)                   # Faint translucent overlay to create a "trail" effect

    if display_mode=="text":                                                 # In text mode: drip-feed points into bursts each frame
        for _ in range(PTS_PER_FRAME):
            if text_pts:
                i=int(random(len(text_pts))); x,y,h=text_pts.pop(i)          # Pick a random text point
                bursts.append(Burst(x,y,h))                                  # Turn it into a small burst

    for b in bursts: b.apply(PVector(0,GRAV)); b.update(); b.show()
    bursts[:] = [b for b in bursts if not b.done()]

    if display_mode=="text":
        for r in rockets: r.apply(PVector(0,GRAV)); r.update(); r.show()
        rockets[:] = [r for r in rockets if not r.done()]

    # detect shape finished, then switch to text after delay (for Jan 1)
    if display_mode == "shape" and special_after_text:
        if shape_done_frame == -1 and len(bursts) == 0:
            shape_done_frame = frameCount
        if shape_done_frame != -1 and (frameCount - shape_done_frame) >= special_delay_frames:
            display_mode = "text"
            TEXT_STRING = special_after_text
            special_after_text = None
            shape_done_frame = -1
            bursts[:]=[]; rockets[:]=[]; background(0)
            gen_text_points(TEXT_STRING)

    draw_calendar()

# ---------- Mouse Interaction ----------
def mousePressed():
    global curM, curY
    # header buttons
    x,y,w,h = prev_rect                                                   # Check if the "Prev" button is clicked
    if x<=mouseX<=x+w and y<=mouseY<=y+h:
        if curM==1: curM=12; curY-=1                                      # Go to previous year
        else: curM-=1                                                     # Go to previous month
        return
    
    x,y,w,h = next_rect                                                   # Check if the "Next" button is clicked
    if x<=mouseX<=x+w and y<=mouseY<=y+h:
        if curM==12: curM=1; curY+=1
        else: curM+=1
        return

    if CAL_X<=mouseX<CAL_X+7*CELL_W and CAL_Y<=mouseY<CAL_Y+6*CELL_H:     # Check if a calendar cell is clicked
        c = int((mouseX-CAL_X)/CELL_W); r = int((mouseY-CAL_Y)/CELL_H)
        first_wd, daysInMonth = calendar.monthrange(curY, curM)
        d = r*7+c - first_wd + 1
        if 1<=d<=daysInMonth: apply_pick(curM,d)
        return
