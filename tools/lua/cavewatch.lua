-- Poll the code caves each frame against the built EXE: once a cave matches (EXE loaded), log when a byte changes,
-- with a screenshot. EXE_FILE = built EXE path (--var), WATCH = {{addr, len}, ...} (default: the B_MAIN caves).
local ffi = require('ffi')
local W = WATCH or { { 0x800D1C00, 576 }, { 0x800CF900, 932 }, { 0x800D61FC, 512 } }
local f = io.open(EXE_FILE, 'rb')
local exe = f:read('*a')
f:close()
local ref, hits = {}, 0
L.on_frame(function(n)
  local m = PCSX.getMemPtr()
  for k, w in ipairs(W) do
    local cur = ffi.string(m + (w[1] - 0x80000000), w[2])
    local want = exe:sub(0x800 + (w[1] - 0x80010000) + 1, 0x800 + (w[1] - 0x80010000) + w[2])
    if not ref[k] then
      if cur == want then ref[k] = cur end
    elseif cur ~= ref[k] and hits < 8 then
      hits = hits + 1
      local d = {}
      for i = 1, #cur do if cur:byte(i) ~= ref[k]:byte(i) then d[#d + 1] = string.format('%X', w[1] + i - 1) end end
      L.log(string.format('frame %d cave %d changed at %s', n, k, table.concat(d, ' ', 1, math.min(#d, 12))))
      L.shot('cave_' .. hits)
      ref[k] = cur
    end
  end
end)
