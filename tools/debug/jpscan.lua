-- Runtime leftover-Japanese scan: look at the text of every open window (B_MAIN window array at 0x80149B08, 64 x 0x3CC,
-- buffer at +0xA, FFFF-terminated 16-bit units) and log windows that hold kana/kanji codes (0x57-0xFF, 0x180-0x2DF;
-- 0x100-0x17F are English glyphs, 0x4000+ packed English). Log line: `JP <tag> w<N> <hex units>`.
-- Load before scene.lua / msgs.lua: they call JPSCAN(tag).
local WIN, STRIDE = WIN or 0x80149B08, 0x3CC
function JPSCAN(tag)
  local m = PCSX.getMemPtr()
  for w = 0, 63 do
    local base = (WIN - 0x80000000) + w * STRIDE
    if m[base] % 2 == 1 then -- in use
      local units, bad, skip = {}, false, 0
      for k = 0, 400 do
        local o = base + 0xA + 2 * k
        local u = m[o] + m[o + 1] * 256
        if u == 0xFFFF or u == 0xFFFD then break end -- the expander ends a message with FFFD; the rest is stale
        units[#units + 1] = string.format('%04X', u)
        if skip > 0 then skip = skip - 1 -- an argument of a control code (face id 0x00FF is not kana)
        elseif u == 0xFFEF or u == 0xFFEB or u == 0xFFFC then skip = 1
        elseif u == 0xFFF9 then skip = 2
        elseif (u >= 0x57 and u <= 0xFF) or (u >= 0x180 and u <= 0x2DF) then bad = true end
      end
      if bad then L.log(string.format('JP %s w%d %s', tag, w, table.concat(units, ' ', 1, math.min(#units, 40)))) end
    end
  end
end
