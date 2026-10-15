-- Scene player for tools/debug/tour.py (condition-based waits; fixed frame counts drift with disc loading and RNG).
-- STEPS: list of strings (global set by --var): 'wait N' | 'KEY[*N]' | 'shot' | 'until X Y R G B' | 'mash KEY X Y R G B'.
-- Pixels are compared on the 8-bit values of the 5-bit screen colour, tolerance 12 per channel.
local ffi = require('ffi')
local GAP, TOL, LIMIT = 40, 12, 3000
local i, wait, nshot, tries, since = 1, 0, 0, 0, 0

local function px(x, y)
  local s = PCSX.GPU.takeScreenShot()
  local v = ffi.cast('uint16_t*', s.data.data)[y * tonumber(s.width) + x]
  return (v % 32) * 8, (math.floor(v / 32) % 32) * 8, (math.floor(v / 1024) % 32) * 8
end
local function match(x, y, r, g, b)
  local pr, pg, pb = px(x, y)
  return math.abs(pr - r) <= TOL and math.abs(pg - g) <= TOL and math.abs(pb - b) <= TOL
end
local function nums(t, from) local o = {} for k = from, #t do o[#o + 1] = tonumber(t[k]) end return o end

L.on_frame(function(n)
  if wait > 0 then wait = wait - 1 return end
  if not L.route_done() then return end
  local s = STEPS[i]
  if not s then L.log('scene done at ' .. n) L.finish(0) return end
  local t = {}
  for w in s:gmatch('%S+') do t[#t + 1] = w end
  local c = t[1]
  if c == 'wait' then wait = tonumber(t[2]) i = i + 1
  elseif c == 'shot' then L.shot(string.format('s%02d.png', nshot)) nshot = nshot + 1 i = i + 1
  elseif c == 'until' or c == 'mash' then
    local k = c == 'mash' and 3 or 2
    local p = nums(t, k)
    since = since + 1
    if n % 4 == 0 and match(p[1], p[2], p[3], p[4], p[5]) then
      i = i + 1 since = 0 tries = 0
    elseif since > LIMIT then
      L.shot('timeout.png') -- what the screen looked like when the condition never matched
      L.fail('timeout at step ' .. s)
    elseif c == 'mash' and since % 90 == 1 then
      L.press(t[2], 6)
    end
  else
    local key, rep = t[1]:match('^([^*]+)%*?(%d*)$')
    for _ = 1, tonumber(rep) or 1 do L.press(key, 6) L.press('-', GAP) end
    i = i + 1
  end
end)
