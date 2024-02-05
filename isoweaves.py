# Iso weaves

# Plains
#  - frst: 10 or 11 (lower left warp is on or off)
#  - scnd: number of ons/offs or offs/ons(if first=11) until end of repeat in first column of weave
#  - thrd: horizontal repeats of scnd pattern
#  - frth: 00 means normal plain weave step for pattern. else rise by count . e.g. 01
# for twills, same, for satins same.
# note can have (satin) 7 high can have 6 values in frth section

# frst: must be  in [10,11,20,21,30,31]
#  - when over digits - highlight sq
# scnd: seq of on/off|off/on. total = height of weave
#  - highlight the first column
# thrd: seq of H repeats.
#  - Twills only allow single value here
# frth: how many to rise up before repeating.
#  - plains only allow 00
#  - twills only allow single value
# - each number can be mouse scrolled up or down to limits (-ve might mean %mod)

# if user defines size of region, then show limits under each section.
# if not then show: width,height, %warp cover, %warp,weft activity, longest floats (F,B,W,W)


###
# Show a grid with ISO to the right.
# Underneath grid show: dimensions, weft% etc
# Underneath ISO show: Variation button and 9 sample grids when pressed
#
# Grid - not editable (later and calc ISO from contents)
# Info area - not editable (later can we set w,h)
# ISO value:
#  - show four values separated by '-'
#    - +/- button over 2,3,4 to add numbers (where legal),
#    - mousewheel to inc/dec value
#    - random button under each which changes value/add values
#  - mouseover = highlight(outline) area that will change
#    - 01 - remember settings for each of three types independently
#    - 02 - +/- button above to add/del values in seq. draw simple region outline
#    - 03 - Plain allows multiple values. rest are single value
#    - 04 - Plain ignore, Satin +/- allow multiple values.
#         - for each multiple value - highlight outline area when over it.
#  - mousewheel on value - increase/decrease value and recalc.
#    Check valid and stop/skip if not.
# Variation button
#  - Perturb type and show 9 variants maybe with numbers. Selecting one refocuses UI.


import svg as SVG

wif_parts = ["""[WIF]\nVersion=1.1\nDate=April 20, 1997\nDevelopers=wif@mhsoft.com\nSource Program=ISOweave online\n
Source Version=1.0\n\n[CONTENTS]\nCOLOR PALETTE=true\nTEXT=true\nWEAVING=true\nWARP=true\nWEFT=true\n
COLOR TABLE=true\nTHREADING=true\nTIEUP=true\nTREADLING=true\n\n[TEXT]\nTitle=""",
            #1{self.label}
            "\n\n[THREADING]\n",
            #3 threading count seq 1=1
            "\n[TIEUP]\n",
            # tieup count seq
            #1=1,2,4
            #2=2,3,5
            #3=1,3,4
            "\n[TREADLING]\n",
            #4 treadling count seq 1=1
            "[WEAVING]\nRising Shed=true\nTreadles=",
            #5{self.width}
            "\nShafts=",
            #6{self.height}
            "\n\n[WARP]\nUnits=centimeters\nColor=0\nThreads=",
            #7{self.height}
            "\nSpacing=0.212\nThickness=0.212\n\n[WEFT]\nUnits=centimeters\nColor=1\nThreads=",
            #8{self.width}
            "\nSpacing=0.212\nThickness=0.212\n\n[COLOR TABLE]\n1=255,255,255\n2=0,0,0\n\n[COLOR PALETTE]\nRange=0,255\nEntries=2\n"
           ]

##
samples = ["10-01 01-01-00", "10-01 01-02-00", "10-04 02-01-00",
           "10-04 02-04 02-00", "20-03 01-01-03", "21-01 03-01-01",
           "21-03 01-01-03", "20-01 03-01-01", "20-03 04-01-06",
           "20-02 01 01 02-01-01", "20-05 02-01-02",
           "20-05 01 01 02-01-02", "20-01 04-02-01", 
           "30-01 06-01-02",
           "30-01 07-01-03", "30-07 01-01-05", "30-05 01-01-03 04 04 03 02",
           "30-07 01-01-05",
           #
           "10-01 01-01-00", "10-03 03-01-00", "10-01 01-02-00",
           "10-02 02-02-00", "10-03 02-02 01-00", "20-01 05-01-01",
           "10-03 01 02 02 01 01 01 01-03 01 02 02 01 01 01 01-00",
           "20-03 02 01 02-01-02", "20-05 03-01-07", "20-03 01 02 02 01 03-01-01",
           # "20-02 01 01 02 01 03-01-01", "20-03 03-01-01",
           #
           # "20-01 05-02-01",  # thrd > 1
           # "20-03 03-01-01 02 05 04 03",  # multiple frth
           # "30-07 01-02-05",  # thrd > 1
           # "31-02 03 02 01-01-02 03 02 03 04 02 03"
           ]

def shift(warplist, count):
    """
    Shift an array to the right by count 
    - wrap using modulus
    """
    warplen = len(warplist)
    result = [0 for i in range(warplen)]
    for i in range(warplen):
        newpos = i+count
        result[newpos % warplen] = warplist[i]
    return result


def invert(warplist):
    """
    Invert the values in the list
    - values are 0 or 1
    """
    return [1-val for val in warplist]


class Pattern_grid(object):
    """
    Hold an array of 0,1 values for the iso pattern.
    Also hold an SVG representation for use
    """
    def __init__(self, width, height, repeats=1):
        self.width = width
        self.height = height
        self.cols = [[0 for y in range(height)] for x in range(width)]
        self.diagram = None  # svg

    def __repr__(self):
        print("<Pattern: %dx%d>" % (self.width, self.height))

    def _repr_svg_(self):
        return self.diagram.outerHTML

    def svg(self):
        return self._repr_svg_()

    def calc_floats(self):
        """
        Calculate warp and weft float maximums
        """
        weft_count = 0
        warp_count = 0
        max_zeros, max_ones, prev, zero, one = 0,0,2,0,0
        # check the columns
        for x in range(self.width):
            col = self.cols[x]
            weft_count += sum(col)
            warp_count += len(col)-sum(col)
            for v in col:
                if v == prev:
                    if v == 0: zero += 1
                    else: one += 1
                else:
                    if zero > max_zeros: max_zeros = zero
                    if one > max_ones: max_ones = one
                    zero,one,prev = 0,0,v
            if zero > max_zeros: max_zeros = zero
            if one > max_ones: max_ones = one
            zero,one,prev = 0,0,2
        max_warp = max(max_zeros, max_ones)
        # check the rows
        max_zeros, max_ones, prev, zero, one = 0,0,2,0,0
        for row in self.rows:
            for v in row:
                if v == prev:
                    if v == 0: zero += 1
                    else: one += 1
                else:
                    if zero > max_zeros: max_zeros = zero
                    if one > max_ones: max_ones = one
                    zero,one,prev = 0,0,v
            if zero > max_zeros: max_zeros = zero
            if one > max_ones: max_ones = one
            zero,one,prev = 0,0,2
        #
        max_weft = max(max_zeros, max_ones)
        return [max_warp, max_weft], [weft_count, warp_count]

    def calc_rows(self):
        """
        remap the primary cols ordering into a rows ordering.
        For use in show() and calc_floats()
        """
        self.rows = []
        for y in range(self.height-1,-1,-1):
            self.rows.append([self.cols[x][y] for x in range(self.width)])
            
    def show(self):
        """
        A simple Printed X,O representation
        """
        for row in self.rows:
            line = [['0','X'][value] for value in row]
            print(line)

    def create_wif(self, label):
        """
        Package up as a straight draw no-repeat draft
        """
        wif_data = wif_parts[0]+label+wif_parts[1]
        # Threading (height)
        wif_data += "".join([f"{i}={i}\n" for i in range(1,self.height+1)])
        wif_data += wif_parts[2]
        # Tieup
        for i,col in enumerate(self.cols):
            line = ",".join([str(j+1) for j,idx in enumerate(range(len(col))) if col[idx]==1])
            wif_data += f"{i+1}={line}\n"
        wif_data += wif_parts[3]
        # Treadling (width)
        wif_data += "".join([f"{i}={i}\n" for i in range(1,self.width+1)])
        wif_data += wif_parts[4] + str(self.width)
        wif_data += wif_parts[5] + str(self.height)
        wif_data += wif_parts[6] + str(self.height)
        wif_data += wif_parts[7] + str(self.width) + wif_parts[8]
        return wif_data
        
 
    def create_isogrid(self, canvas, offset, boxstyle, clearstyle, box_sq, id=0):
        """
        Build a single boxes only representation of the pattern
        Use diff styles to show repeats vs core
        """
        draft = SVG.g()
        canvas.appendChild(draft)
        #
        for yy,warp in enumerate(range(self.height-1,-1,-1)):
            for xx,weft in enumerate(range(self.width)):
                value = self.cols[weft][warp]
                box = SVG.rect(x=offset[0] + xx*box_sq, y=offset[1] + yy*box_sq,
                               width=box_sq, height=box_sq,
                               id=str(id)+"_"+str(xx)+"_"+str(yy),
                               style=[clearstyle, boxstyle][value])
                draft.appendChild(box)
        
    def build_svg(self, label, dimensions = [600,500], repeats=2,
                  box_sq=10, linewidth=1, box_colors=["red","gray"]):
        """
        Build an SVG representaion of the grid
        - with repeats
        """
        box_off_style = {"fill":"white", "stroke": "black", "stroke-width": str(linewidth)+"px"}
        box_on_style = {"fill":"none", "stroke": "black", "stroke-width": str(linewidth)+"px"}
        self.diagram = SVG.svg(width=dimensions[0], height=dimensions[1],
                          preserveAspectRatio="xMidYMid meet",
                          viewBox="0 0 {} {}".format(dimensions[0], dimensions[1]))
        self.canvas = SVG.g()
        self.diagram.appendChild(self.canvas)
        #
        offsets = [0, 0]
        if label:
            title = SVG.text(label, x=20,y=18, id="labeltxt")
            self.canvas.appendChild(title)
            offsets = [20,30]
        #
        count = 0
        for y in range(repeats):
            for x in range(repeats):
                offset = [offsets[0] + x * self.width*box_sq, offsets[1] + y * self.height*box_sq]
                if x==0 and y==repeats-1:
                    box_on_style["fill"] = box_colors[0]
                else:
                    box_on_style["fill"] = box_colors[1]
                self.create_isogrid(self.canvas, offset, box_on_style, box_off_style, box_sq, id=count)
                count += 1

    def save_diagram(self, filename):
        """
        Save the SVG to a file
        """
        with open(filename, "w") as f:
            f.write(self.diagram.outerHTML)
    


class ISO_pattern(object):
    """
    Holds a drawn representation of the iso format
    """
    def __init__(self, id="21-01 03-01-01"):
        self.id = id
        # Hold each part of the iso representation
        self.frst = 10
        self.scnd = []
        self.thrd = []
        self.frth = []
        self.height = 0
        self.width = 0
        self.history_count = 20
        self.history = []
        self.grid = None  # Holds the pattern and an SVG representation
        #
        self.deconstruct_iso()  # extract the pieces, width etc
        self.build_grid()  # build the visual pattern as SVG
        self.grid.calc_rows()

    def deconstruct_iso(self):
        """
        Separate out the pieces of the format
        Calculate the size
        """
        pieces = self.id.strip().split("-")
        assert(len(pieces) == 4)
        self.frst = int(pieces[0])
        self.scnd = [int(a) for a in pieces[1].strip().split(" ")]
        self.thrd = [int(a) for a in pieces[2].strip().split(" ")]
        self.frth = [int(a) for a in pieces[3].strip().split(" ")]
        self.height = sum(self.scnd)
        self.width = self.calc_width()  # either thrd* height if single number, or sum(thrd)
        self.history = [[self.frst,self.scnd,self.thrd,self.frth]]

    def validate(self):
        """
        check if valid
        - return True/False and report
        """
        pass

    def __repr__(self):
        frst = "%02d" % self.frst # 10,11,20,21,30,31
        scnd = " ".join(["%02d"%a for a in self.scnd])
        thrd = " ".join(["%02d"%a for a in self.thrd])
        frth = " ".join(["%02d"%a for a in self.frth])
        return "<ISO: %s-%s-%s-%s  wxh:%dx%d>" % (frst,scnd,thrd,frth, self.width, self.height)

    def calc_width(self):
        """
        The structure of the iso allows for size determination before interpretation
        - 10,11 - frth = 00
        - 20,21 - thrd = single only, frth single (must tile)-shortest tile
        - 30,31 - thrd = single only, frth single/mult must result in tiling
        """
        # Plain weaves
        if self.frst in [10,11]:
            if len(self.thrd) == 1:
                return self.thrd[0] * len(self.scnd)
            else:
                return sum(self.thrd)
        # Twills
        elif self.frst in [20,21]:
            basic_width = self.thrd[0] * self.height
            if len(self.frth) == 1:
                return basic_width
            else:  # several frth values  #!twill expansion
                min_rpt_width = 1
                # manually find LCM !!works but sheesh
                #while min_rpt_width < basic_width * self.frth[0]:
                #    if (min_rpt_width * self.frth[0]) % basic_width == 0:
                #        break
                #    min_rpt_width += 1
                min_rpt_width = sum(self.thrd) * (len(self.frth) + 1)
                return min_rpt_width
        # Satins
        else:  # frst == 30,31
            if len(self.frth) == 1:
                return self.thrd[0] * sum(self.scnd)
            else:  # multiple 4ths
                return sum(self.thrd) * (len(self.frth) + 1)
    
    def build_grid(self):
        """
        Turn ISO description into a draft
        - define the Pattern_grid()
        """
        self.grid = Pattern_grid(self.width, self.height)
        # frst (on or off)
        dot = 0
        if self.frst % 2 == 0:
            dot = 1
        # create first column
        col = []
        for step in self.scnd:
            col.extend([dot]*step)
            dot = 1-dot # toggle dot each step
        self.grid.cols[0] = col
        # print("first col:",col)
        # Subsequent cols
        #
        # Plain weaves
        if self.frst in [10,11]:
            # thrd is a repeat (single) or series (multiple)
            # frth is always 0 - ignore
            refl_pos = 1  # where do the reflections start
            if len(self.thrd) == 1:
                # a single value in thrd
                if self.thrd[0] == 1:
                    # use the first col
                    refl_pos = 1
                if self.thrd[0] > 1:
                    # repeat the first col
                    for i in range(1, self.thrd[0]):
                        self.grid.cols[i] = col  #self.grid.cols[0]
                    refl_pos = self.thrd[0]
                # reflect
                for i in range(refl_pos, self.width):
                    self.grid.cols[i] = invert(self.grid.cols[0])
            # more than one number in thrd
            else:
                # repeat col by the first number and invert for following counts
                idx = 0
                for count in self.thrd:
                    for i in range(count):
                        self.grid.cols[idx] = col
                        idx += 1
                    col = invert(col)
        # Twills
        elif self.frst in [20,21]:
            # make the repeat then paste and rise.
            rep_pos = 1
            idx = 1
            rise = 0
            if len(self.thrd) != 1:
                print("whoops - Twill - Expecting a single number in third slot")
            else:  # a single value in thrd
                if self.thrd[0] == 1:
                    # get the first col
                    rep_pos = 1
                if self.thrd[0] > 1:
                    # repeat the first col
                    for i in range(self.thrd[0]):
                        self.grid.cols[idx] = col
                        rep_pos = self.thrd[0]
                        idx += 1
                # repeat from rep_pos
                if len(self.frth) == 1:
                    for x in range(rep_pos, self.width, self.thrd[0]):   
                        rise += self.frth[0]
                        for i in range(rep_pos):
                            self.grid.cols[x+i] = shift(self.grid.cols[i], rise)
                else:  # multiple frths   #!twill expansion
                    #print("Whoops - Twill - Expecting a single number in fourth slot")
                    for i,x in enumerate(range(rep_pos, self.width, self.thrd[0])):
                        rise += self.frth[i]
                        for i in range(rep_pos):
                            self.grid.cols[x+i] = shift(self.grid.cols[i], rise)
                        
        # Satins
        elif self.frst in [30,31]:
            rep_pos = 1
            idx = 1
            rise = 0
            if len(self.thrd) != 1:
                print("whoops - Satins - Expecting a single number in third slot")
            else:  # a single value in thrd
                if self.thrd[0] == 1:
                    # get the first col
                    rep_pos = 1
                if self.thrd[0] > 1:
                    # repeat the first col
                    for i in range(self.thrd[0]):
                        self.grid.cols[idx] = col
                        rep_pos = self.thrd[0]
                        idx += 1
                # repeat from rep_pos
                if len(self.frth) == 1:
                    for x in range(rep_pos, self.width, self.thrd[0]):   
                        rise += self.frth[0]
                        for i in range(rep_pos):
                            self.grid.cols[x+i] = shift(self.grid.cols[i], rise)
                else:  # multiple frths
                    for i,x in enumerate(range(rep_pos, self.width, self.thrd[0])):
                        rise += self.frth[i]
                        for i in range(rep_pos):
                            self.grid.cols[x+i] = shift(self.grid.cols[i], rise)

    def info(self):
        """
        type, size, floats, S or Z twill
        """
        square = "(square)" if self.width == self.height else ""
        lines = ""
        mode = ["Plain","Twill","Satin"][int(self.frst/10)-1]  #! and S/Z for Twill
        width = self.calc_width()
        floats,dominance = self.grid.calc_floats()
        lines += f"{mode} pattern: {square}\n- dimensions (width,height): {self.width}, {self.height}"
        lines += f"\n- longest Floats (warp,weft): {floats[0]}, {floats[1]}"
        if dominance[0] == dominance[1]:
            lines += "\n- balanced weave."
        elif dominance[0] >= dominance[1]:
            lines += "\n- warp faced weave."
        else:
            lines += "\n- weft faced weave."
        return lines

if __name__ == "__main__":
    iso = ISO_pattern("30-02 04-01-02")
    print(iso)
    iso.grid.show()
    print()
    # for s in samples:
        # iso = ISO_pattern(s)
        # print(iso)
        # iso.grid.show()
        # iso.grid.build_svg(s, repeats=2)
        # iso.grid.save_diagram("foo.svg")
    print(iso.info())

## probably don't need below for UI as we can draw ontop and no click feedback
# Build a grid of size N. id each grid cell
# - write into the grid
# - accessors for frst, each scnd, thrd, frth areas
