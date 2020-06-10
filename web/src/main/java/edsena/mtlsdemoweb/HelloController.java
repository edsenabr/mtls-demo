package edsena.mtlsdemoweb;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.http.ResponseEntity;
import javax.servlet.http.HttpServletRequest;

@RestController
public class HelloController {
	@GetMapping(path = "/")
	public ResponseEntity<Map<String, String>> getCallerAddress(HttpServletRequest request) {
		Map<String, String> headers = new HashMap<>();
		headers.put("x-forwarded-for", request.getHeader("x-forwarded-for"));
		headers.put("remote_address", request.getRemoteAddr());
		return  ResponseEntity.ok(headers);
	}

	@GetMapping(path = "/all")
	public ResponseEntity<Map<String, List<String>>> getAllHeaders(HttpServletRequest request) {
		return ResponseEntity.ok(
			Collections
				.list(request.getHeaderNames())
				.stream()
				.collect(Collectors.toMap(
					Function.identity(), 
					h -> Collections.list(request.getHeaders(h))
				))
		);
	}
}