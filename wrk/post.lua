local json = require("json")

function getDate(offset)
  local secondsInDay = 24 * 60 * 60
  return os.date("!%Y-%m-%d", os.time() + offset * secondsInDay)
end

local headers = {}
headers["Content-Type"] = "application/json"

function request()
  startday = math.random(1, 30)
  endday = math.random(startday + 1, startday + 10)

  local data = {
    ["start"] = getDate(startday),
    ["end"] = getDate(endday),
    ["room_id"] = math.random(1,3)
  }
  return wrk.format("POST", "/api/v1/bookings/", headers, json.encode(data))
end

-- -- tracing responses
-- function response(status, headers, body)
--   print(status, body)
-- end

