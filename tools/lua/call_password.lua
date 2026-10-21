-- Vine Center password screen check: from a field state, call B_MAIN 0x8002119C(PW = answer index 0-6) through
-- tools/debug/hijack.lua, let tools/debug/scene.lua type the answer, log the game's verdict (v0 = 1 match).
--   --script tools/debug/hijack.lua --script tools/debug/scene.lua --var STEPS=... --script tools/lua/call_password.lua --var PW=0
local FN = PW_FN or 0x8002119C
L.on_frame(function(n)
  if n == 10 then H.call(FN, PW or 0)
  elseif n > 10 and H.count == 1 then
    L.log(string.format('password %d: v0 = %d', PW or 0, H.ret))
    L.shot('result.png')
    H.count = 2
  end
end)
