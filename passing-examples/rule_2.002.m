close all
clear
% Nested functions not allowed but compound statements ok
function outer
  a = (-20:100)
  b = 1
  for i = 1:10
    if a[i] == 0
      b = b + 2
    end
  end

end

function second
  a = (1:10)
  a(end + 1) = 3
end
