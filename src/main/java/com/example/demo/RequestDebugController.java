package com.example.demo.controller;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.*;

@RestController
public class RequestDebugController {

    @RequestMapping(value = "/debug", 
        method = {RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT, RequestMethod.DELETE},
        produces = MediaType.APPLICATION_JSON_VALUE)
    public Map<String, Object> debugRequest(HttpServletRequest request) throws IOException {
        // 디버그 정보를 저장할 맵 생성
        Map<String, Object> debugInfo = new HashMap<>();

        // 요청 메서드 추가
        debugInfo.put("method", request.getMethod());

        // 전체 헤더 정보 수집
        Map<String, String> headers = new HashMap<>();
        Enumeration<String> headerNames = request.getHeaderNames();
        while (headerNames.hasMoreElements()) {
            String headerName = headerNames.nextElement();
            headers.put(headerName, request.getHeader(headerName));
        }
        debugInfo.put("headers", headers);

        // 쿼리 파라미터 수집
        Map<String, String[]> queryParams = request.getParameterMap();
        debugInfo.put("queryParams", queryParams);

        // 요청 바디 수집 (수동 읽기)
        String body = request.getReader().lines()
            .reduce("", (accumulator, actual) -> accumulator + actual);
        
        debugInfo.put("body", body.isEmpty() ? "No request body" : body);

        // 기타 요청 정보
        debugInfo.put("requestURL", request.getRequestURL().toString());
        debugInfo.put("remoteAddr", request.getRemoteAddr());
        debugInfo.put("contentType", request.getContentType());

        return debugInfo;
    }

    @Component
    public class RequestCachingFilter extends OncePerRequestFilter {
        @Override
        protected void doFilterInternal(HttpServletRequest request, 
                                        HttpServletResponse response, 
                                        FilterChain filterChain) 
                                        throws ServletException, IOException {
            // 요청 본문을 여러 번 읽을 수 있도록 래퍼로 변환
            ContentCachingRequestWrapper wrappedRequest = 
                new ContentCachingRequestWrapper(request);
            ContentCachingResponseWrapper wrappedResponse = 
                new ContentCachingResponseWrapper(response);

            try {
                filterChain.doFilter(wrappedRequest, wrappedResponse);
            } finally {
                // 응답 내용 복사
                wrappedResponse.copyBodyToResponse();
            }
        }
    }
}