-- Show dialogue messages one by one through the game's own event VM and shoot every page.
-- Needs hijack.lua first. Globals: IDS = message ids (3000+ = event overlay table, below = B_MAIN table), TAG = file
-- prefix, FIRST/LAST (1-based indexes into IDS, optional).
-- Per message: write a 2-op script (0x14 <id> = show message, 0x7E = end) to free RAM and run the VM on it
-- (B_MAIN 0x800262F4). When the box has stopped changing (typing done, waiting for a key) shoot s<id>_<page>.png and
-- press circle. The VM draws and closes the box itself.
local ffi = require('ffi')
local SCRIPT = 0x8014F100
local i, page, last, same, hold, started = FIRST or 1, 0, nil, 0, 0, false
local LASTI = LAST or #IDS

local function boxhash()
  local s = PCSX.GPU.takeScreenShot()
  local p, w = ffi.cast('uint16_t*', s.data.data), tonumber(s.width)
  local h = 0
  for y = 150, 218, 2 do -- three text lines; the blinking arrow sits at x 114-138, y 200+
    for x = 10, 245, 2 do
      if y < 200 or x < 114 or x > 138 then h = (h * 31 + p[y * w + x]) % 4294967296 end
    end
  end
  return h
end

L.on_frame(function(n)
  if n < 20 then return end
  if i > LASTI then L.log('msgs done ' .. LASTI) L.finish(0) return end
  if not L.route_done() then return end
  if not started then
    local m, id = PCSX.getMemPtr(), IDS[i]
    local o = SCRIPT - 0x80000000
    local b = { 0x15, 0, 0, 0, 0x14, 0, id % 256, math.floor(id / 256), 0x16, 0, 0, 0, 0x7E, 0, 0, 0 }
    for k = 1, #b do m[o + k - 1] = b[k] end
    H.call(VM or 0x800262F4, SCRIPT)
    started, page, last, same, hold = true, 0, nil, 0, 0
    return
  end
  if H.done() then -- the message ended: next one
    local m = PCSX.getMemPtr()
    local pc = m[0xD7BA0] + m[0xD7BA1] * 256 + m[0xD7BA2] * 65536 + m[0xD7BA3] * 16777216
    L.log(string.format('id %d: %d pages, %d frames, vm pc %08X, 7b9f=%02X 7bec=%02X', IDS[i], page, hold, pc, m[0xD7B9F],
      m[0xD7BEC]))
    i, started = i + 1, false
    return
  end
  hold = hold + 1
  if hold % 6 ~= 0 then return end
  local h = boxhash()
  same = (h == last) and same + 1 or 0
  last = h
  if same >= 4 then -- stable: typing finished, waiting for the key
    L.shot(string.format('%s%04d_%d.png', TAG or 'm', IDS[i], page))
    if JPSCAN then JPSCAN(string.format('%d_%d', IDS[i], page)) end
    page, same, last = page + 1, 0, nil
    L.press('circle', 6) L.press('-', 24)
  elseif hold > 2400 then
    L.log('stuck id ' .. IDS[i])
    L.shot(string.format('%s%04d_stuck.png', TAG or 'm', IDS[i]))
    L.press('circle', 6) L.press('-', 24)
    hold = 0
  end
end)
